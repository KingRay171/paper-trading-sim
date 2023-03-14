import yahooquery as yq

print(yq.Screener().get_screeners('most_actives', 100))
