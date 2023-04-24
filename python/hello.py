class Pin:
  OUT = "OUT"

  def __init__(self, id_, mode=None):
    self.id = id_
    self.value = None

  def value(self, value_to_set=None):
    import pdb; pdb.set_trace()
    if value_to_set is not None:
      # print(f"Setting pin {self.id} to {value_to_set}")
      self.value = value_to_set
    else:
      return self.value
