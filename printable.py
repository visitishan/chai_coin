class Printable:
	"""docstring for Printable __init__(self, arg):
		super Printable__init__()
		self.arg = arg"""
	def __repr__(self):
		return str(self.__dict__)