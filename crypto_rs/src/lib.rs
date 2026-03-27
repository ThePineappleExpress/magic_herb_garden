//! crypto_rs - AES-256-GCM encryption and PBKDF2-HMAC-SHA256 primitives
//! exposed to Python via PyO3 for Magic Herb Tracker.
//!
//! Wire format produced by encrypt_bytes():
//!     b"ENC1"          (4-byte magic)
//!     nonce            (12 bytes, OS-random per call)
//!     ciphertext+tag   (variable length, AES-256-GCM output)
//!
//! All functions map 1-to-1 with the previous cryptography-package API so
//! crypto.py, helpers.py, and weed_format.py can be thin callers without
//! any behaviour changes.

use aes_gcm::{
    aead::{Aead, KeyInit, Payload},
    Aes256Gcm, Nonce,
};
use pbkdf2::pbkdf2_hmac;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use rand::RngCore;
use sha2::Sha256;
use subtle::ConstantTimeEq;

const MAGIC: &[u8; 4] = b"ENC1";
const IV_LEN: usize = 12; // 96-bit GCM nonce

// -- is_encrypted -------------------------------------------------------------

/// Return True if *data* begins with the ENC1 magic header.
#[pyfunction]
fn is_encrypted(data: &[u8]) -> bool {
    data.len() >= 4 && &data[..4] == MAGIC
}

// -- encrypt_bytes -------------------------------------------------------------

/// Encrypt *plaintext* with AES-256-GCM using a fresh OS-random nonce.
///
/// *aad* (Additional Authenticated Data) is optional; when supplied the
/// ciphertext is cryptographically bound to that context (e.g. a file path)
/// and cannot be silently transplanted elsewhere.
///
/// Returns the ENC1-prefixed binary blob: magic (4) + nonce (12) + ct+tag.
#[pyfunction]
#[pyo3(signature = (plaintext, key, aad=None))]
fn encrypt_bytes<'py>(
    py: Python<'py>,
    plaintext: &[u8],
    key: &[u8],
    aad: Option<&[u8]>,
) -> PyResult<Bound<'py, PyBytes>> {
    if key.len() != 32 {
        return Err(PyValueError::new_err(format!(
            "Key must be 32 bytes, got {}",
            key.len()
        )));
    }

    let cipher = Aes256Gcm::new_from_slice(key)
        .map_err(|e| PyValueError::new_err(e.to_string()))?;

    let mut nonce_bytes = [0u8; IV_LEN];
    rand::rngs::OsRng.fill_bytes(&mut nonce_bytes);
    let nonce = Nonce::from_slice(&nonce_bytes);

    let ciphertext = match aad {
        Some(aad_bytes) => cipher.encrypt(nonce, Payload { msg: plaintext, aad: aad_bytes }),
        None => cipher.encrypt(nonce, plaintext),
    }
    .map_err(|e| PyValueError::new_err(format!("Encryption failed: {e}")))?;

    let mut result = Vec::with_capacity(4 + IV_LEN + ciphertext.len());
    result.extend_from_slice(MAGIC);
    result.extend_from_slice(&nonce_bytes);
    result.extend_from_slice(&ciphertext);
    Ok(PyBytes::new_bound(py, &result))
}

// -- decrypt_bytes -------------------------------------------------------------

/// Decrypt an ENC1-prefixed blob.  Raises ``ValueError`` on auth failure or
/// missing ENC1 header.  *aad* must match the value used during encryption.
#[pyfunction]
#[pyo3(signature = (data, key, aad=None))]
fn decrypt_bytes<'py>(
    py: Python<'py>,
    data: &[u8],
    key: &[u8],
    aad: Option<&[u8]>,
) -> PyResult<Bound<'py, PyBytes>> {
    if !is_encrypted(data) {
        return Err(PyValueError::new_err(
            "Data does not have ENC1 header - not encrypted by this app",
        ));
    }
    if key.len() != 32 {
        return Err(PyValueError::new_err(format!(
            "Key must be 32 bytes, got {}",
            key.len()
        )));
    }
    if data.len() < 4 + IV_LEN {
        return Err(PyValueError::new_err(
            "Data too short to be valid ciphertext",
        ));
    }

    let nonce = Nonce::from_slice(&data[4..4 + IV_LEN]);
    let ciphertext = &data[4 + IV_LEN..];

    let cipher = Aes256Gcm::new_from_slice(key)
        .map_err(|e| PyValueError::new_err(e.to_string()))?;

    let plaintext = match aad {
        Some(aad_bytes) => cipher.decrypt(nonce, Payload { msg: ciphertext, aad: aad_bytes }),
        None => cipher.decrypt(nonce, ciphertext),
    }
    .map_err(|_| PyValueError::new_err("Decryption failed - wrong key or corrupted data"))?;

    Ok(PyBytes::new_bound(py, &plaintext))
}

// -- pbkdf2_hmac_sha256 --------------------------------------------------------

/// PBKDF2-HMAC-SHA256 key derivation.  Returns *dklen* raw bytes.
///
/// Replaces all ``hashlib.pbkdf2_hmac("sha256", ...)`` calls in helpers.py
/// and weed_format.py.
#[pyfunction]
#[pyo3(signature = (password, salt, iterations, dklen = 32))]
fn pbkdf2_hmac_sha256<'py>(
    py: Python<'py>,
    password: &[u8],
    salt: &[u8],
    iterations: u32,
    dklen: usize,
) -> PyResult<Bound<'py, PyBytes>> {
    let mut dk = vec![0u8; dklen];
    pbkdf2_hmac::<Sha256>(password, salt, iterations, &mut dk);
    Ok(PyBytes::new_bound(py, &dk))
}

// -- generate_salt -------------------------------------------------------------

/// Return *n* cryptographically random bytes from the OS CSPRNG.
///
/// Replaces ``os.urandom(n)`` in password / key derivation paths.
#[pyfunction]
fn generate_salt(py: Python<'_>, n: usize) -> PyResult<Bound<'_, PyBytes>> {
    let mut buf = vec![0u8; n];
    rand::rngs::OsRng.fill_bytes(&mut buf);
    Ok(PyBytes::new_bound(py, &buf))
}

// -- compare_digest_hex --------------------------------------------------------

/// Constant-time comparison of two hex-encoded strings.
///
/// Replaces ``hmac.compare_digest(a, b)`` in verify_password to guard
/// against timing side-channels.  Returns False immediately when lengths
/// differ (length itself is not secret for fixed-length hex hashes).
#[pyfunction]
fn compare_digest_hex(a: &str, b: &str) -> bool {
    let a_bytes = a.as_bytes();
    let b_bytes = b.as_bytes();
    if a_bytes.len() != b_bytes.len() {
        return false;
    }
    bool::from(a_bytes.ct_eq(b_bytes))
}

// -- weed_encrypt_payload / weed_decrypt_payload -------------------------------
//
// The .weed format uses a raw  IV(12) + ciphertext+tag  layout for section
// payloads - no ENC1 prefix.  These are internal to weed_format.py and must
// not be confused with the ENC1-framed functions above.

/// Encrypt *plaintext* with AES-256-GCM; return raw IV (12 bytes) + ct+tag.
/// Used for .weed section payloads.
#[pyfunction]
fn weed_encrypt_payload<'py>(
    py: Python<'py>,
    plaintext: &[u8],
    key: &[u8],
) -> PyResult<Bound<'py, PyBytes>> {
    if key.len() != 32 {
        return Err(PyValueError::new_err(format!(
            "Key must be 32 bytes, got {}",
            key.len()
        )));
    }

    let cipher = Aes256Gcm::new_from_slice(key)
        .map_err(|e| PyValueError::new_err(e.to_string()))?;

    let mut nonce_bytes = [0u8; IV_LEN];
    rand::rngs::OsRng.fill_bytes(&mut nonce_bytes);
    let nonce = Nonce::from_slice(&nonce_bytes);

    let ciphertext = cipher
        .encrypt(nonce, plaintext)
        .map_err(|e| PyValueError::new_err(format!("Encryption failed: {e}")))?;

    let mut result = Vec::with_capacity(IV_LEN + ciphertext.len());
    result.extend_from_slice(&nonce_bytes);
    result.extend_from_slice(&ciphertext);
    Ok(PyBytes::new_bound(py, &result))
}

/// Decrypt a raw IV (12 bytes) + ct+tag blob produced by weed_encrypt_payload.
/// Raises ``ValueError`` on auth failure.
#[pyfunction]
fn weed_decrypt_payload<'py>(
    py: Python<'py>,
    payload: &[u8],
    key: &[u8],
) -> PyResult<Bound<'py, PyBytes>> {
    if key.len() != 32 {
        return Err(PyValueError::new_err(format!(
            "Key must be 32 bytes, got {}",
            key.len()
        )));
    }
    if payload.len() < IV_LEN {
        return Err(PyValueError::new_err(
            "Section payload too short to contain IV",
        ));
    }

    let nonce = Nonce::from_slice(&payload[..IV_LEN]);
    let ciphertext = &payload[IV_LEN..];

    let cipher = Aes256Gcm::new_from_slice(key)
        .map_err(|e| PyValueError::new_err(e.to_string()))?;

    let plaintext = cipher
        .decrypt(nonce, ciphertext)
        .map_err(|_| PyValueError::new_err("Wrong export password or corrupted section payload"))?;

    Ok(PyBytes::new_bound(py, &plaintext))
}

// -- module --------------------------------------------------------------------

#[pymodule]
fn crypto_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(is_encrypted, m)?)?;
    m.add_function(wrap_pyfunction!(encrypt_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(decrypt_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(pbkdf2_hmac_sha256, m)?)?;
    m.add_function(wrap_pyfunction!(generate_salt, m)?)?;
    m.add_function(wrap_pyfunction!(compare_digest_hex, m)?)?;
    m.add_function(wrap_pyfunction!(weed_encrypt_payload, m)?)?;
    m.add_function(wrap_pyfunction!(weed_decrypt_payload, m)?)?;
    Ok(())
}
