"""The kfp_component_lib package."""
VERSION = "0.1.0.dev0"
PKG_DEPENDENCY = [f"kfp_component_lib=={VERSION}", "--find-links=dist"]
KFP_CONTAINER_IMAGE = f"alexioannides/kfp-component-lib:{VERSION}"
