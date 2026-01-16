from kivy.animation import Animation


def shake_and_flash(widget, use_bg=False, use_text=True, flash_color=(0.827, 0.247, 0.286, 1), offset=15):
    from kivy.animation import Animation

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

    orig_color = getattr(widget, color_attr, None)
    anim = shake

    if orig_color is not None:
        color_anim = (
            Animation(**{color_attr: flash_color}, duration=0.05) +
            Animation(**{color_attr: orig_color}, duration=0.05) +
            Animation(**{color_attr: flash_color}, duration=0.05) +
            Animation(**{color_attr: orig_color}, duration=0.05) 
        )
        anim &= color_anim

    anim.start(widget)