# numberSimplifier method simplifies large numbers, such as 152682054 to 152.682 M
def simplify(num):
  # Trillion simplifier
  if (num >= 1000000000000):
    num /= 1000000000000
    num = round(num, 2)
    return str(num) + 'T'
    
  # Billion simplifier
  if (num >= 1000000000):
    num /= 1000000000
    num = round(num, 2)
    return str(num) + 'B'

  # Million simplifier
  if (num >= 1000000):
    num /= 1000000
    num = round(num, 2)
    return str(num) + 'M'

  if (num >= 1000):
    num /= 1000
    num = round(num, 2)
    return str(num) + 'k'


print(simplify(420000343))