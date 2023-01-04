# numberSimplifier method simplifies large numbers, such as 152682054 to 152.682 M
def numberSimplifier(num):
  # Trillion simplifier
  if (num >= 1000000000000):
    num /= 1000000000000
    num = round(num, 3)
    return str(num) + ' T'
    
  # Billion simplifier
  if (num >= 1000000000):
    num /= 1000000000
    num = round(num, 3)
    return str(num) + ' B'

  # Million simplifier
  if (num >= 1000000):
    num /= 1000000
    num = round(num, 3)
    return str(num) + ' M'
