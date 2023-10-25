#!/usr/bin/env python3
from os import listdir
from importlib import import_module
from random import choice as rchoice
from worker import config_dict, LOGGER
from worker.helper.themes import ad_minimal

AVL_THEMES = {}
for theme in listdir('worker/helper/themes'):
    if theme.startswith('ad_') and theme.endswith('.py'):
        AVL_THEMES[theme[5:-3]] = import_module(f'worker.helper.themes.{theme[:-3]}')

def BotTheme(var_name, **format_vars):
    text = None
    theme_ = 'minimal'

    if theme_ in AVL_THEMES:
        text = getattr(AVL_THEMES[theme_].ADWStyle(), var_name, None)
        if text is None:
            LOGGER.error(f"{var_name} not Found in {theme_}.")
    elif theme_ == 'random':
        rantheme = rchoice(list(AVL_THEMES.values()))
        LOGGER.info(f"Random Theme Chosen: {rantheme}")
        text = getattr(rantheme.ADWStyle(), var_name, None)
        
    if text is None:
        text = getattr(ad_minimal.ADWStyle(), var_name)

    return text.format_map(format_vars)
