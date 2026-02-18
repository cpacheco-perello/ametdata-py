"""Paquete principal de aemetdata."""


from .aemet_client import AemetClient
from . import avisos
from . import climatologia
from . import imagenes
from . import observaciones
from . import utils

__all__ = [
	"AemetClient",
	"avisos",
	"climatologia",
	"imagenes",
	"observaciones",
	"utils",
]

