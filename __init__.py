from pathlib import Path
import os
import shutil
import subprocess

def install(module):
    import sys
    try:
        print(f"\033[92m[smZNodes] \033[0;31m{module} is not installed. Attempting to install...\033[0m")
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])
        reload()
        print(f"\033[92m[smZNodes] {module} Installed!\033[0m")
    except:
        print(f"\033[92m[smZNodes] \033[0;31mFailed to install {module}.\033[0m")

# Reload modules after installation
PRELOADED_MODULES = set()
def init() :
    # local imports to keep things neat
    from sys import modules
    import importlib
    global PRELOADED_MODULES
    # sys and importlib are ignored here too
    PRELOADED_MODULES = set(modules.values())
def reload() :
    from sys import modules
    import importlib
    for module in set(modules.values()) - PRELOADED_MODULES :
        try :
            importlib.reload(module)
        except :
            pass
init()

# compel =================
try:
    from compel import Compel
except ImportError:
    install("compel")

# lark =================
try:
    from lark import Lark
except ImportError:
    install("lark")
# ============================

# ==== web ======
cwd_path = Path(__file__).parent
comfy_path = cwd_path.parent.parent
def copy_to_web(file):
    """Copy a file to the web extension path."""
    shutil.copy(file, web_extension_path)

web_extension_path = os.path.join(comfy_path, "web", "extensions", "smZNodes")

smZdynamicWidgets_JS_file = os.path.join(cwd_path, "js", "smZdynamicWidgets.js")

if not os.path.exists(web_extension_path):
    os.makedirs(web_extension_path)
else:
    shutil.rmtree(web_extension_path)
    os.makedirs(web_extension_path)

copy_to_web(smZdynamicWidgets_JS_file)

# ==============

from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

# add_sample_dpmpp_2m_alt, inject_code, opts as smZ_opts
from .smZNodes import add_sample_dpmpp_2m_alt, inject_code

add_sample_dpmpp_2m_alt()

from comfy.samplers import KSampler
injected_code = """
            try:
                if positive[0][1].get('from_smZ', None) or negative[0][1].get('from_smZ', None):
                    from ComfyUI_smZNodes.modules.shared import opts as smZ_opts
                    if smZ_opts.disable_max_denoise:
                        max_denoise = False
                    if positive[0][1].get('use_CFGDenoiser', None) or negative[0][1].get('use_CFGDenoiser', None):
                        from ComfyUI_smZNodes.smZNodes import set_model_k
                        set_model_k(self)
            except Exception as err:
                pass
"""
modified_function = inject_code(KSampler.sample, target_line="self.model_k.noise = noise", code_to_insert=injected_code)
KSampler.sample = modified_function
