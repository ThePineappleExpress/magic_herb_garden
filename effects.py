from kivy.animation import Animation


def shake_and_flash(widget, use_bg=False, use_text=True, flash_color=None, offset=15):
    from kivy.animation import Animation
    from kivy.app import App

    if flash_color is None:
        app = App.get_running_app()
        if app and hasattr(app, 'theme'):
            flash_color = list(app.theme.color_accent_1)
        else:
            flash_color = (0.827, 0.247, 0.286, 1)

    orig_x = widget.x

    shake = (
        Animation(x=orig_x - offset, duration=0.05) +
        Animation(x=orig_x + offset, duration=0.05) +
        Animation(x=orig_x - offset, duration=0.05) +
        Animation(x=orig_x + offset, duration=0.05) +
        Animation(x=orig_x - offset, duration=0.05) +
        Animation(x=orig_x + offset, duration=0.05) +
        Animation(x=orig_x, duration=0.05)
    )

    if use_bg:
        color_attr = "background_color"
    else:
        color_attr = "color"            # for Label/Button
        hint_attr = "hint_text_color"  # for TextInput
    orig_color = getattr(widget, color_attr, None)
    anim = shake
    hint_color = getattr(widget, hint_attr, None)
    if use_text and hint_color is not None:
        orig_hint_color = hint_color
        hint_anim = (
            Animation(**{hint_attr: flash_color}, duration=0.05) +
            Animation(**{hint_attr: orig_hint_color}, duration=0.05) +
            Animation(**{hint_attr: flash_color}, duration=0.05) +
            Animation(**{hint_attr: orig_hint_color}, duration=0.05) 
        )
        anim &= hint_anim
    if orig_color is not None:
        color_anim = (
            Animation(**{color_attr: flash_color}, duration=0.05) +
            Animation(**{color_attr: orig_color}, duration=0.05) +
            Animation(**{color_attr: flash_color}, duration=0.05) +
            Animation(**{color_attr: orig_color}, duration=0.05) 
        )
        anim &= color_anim

    anim.start(widget)