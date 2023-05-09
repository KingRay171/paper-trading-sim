from PySide6.QtGui import QIcon
import os

def update_ticker_icon(data: tuple) -> QIcon:
    """
    Updates the performance icon for the given stock

        ticker : pandas.DataFrame
            A Pandas dataframe representing a ticker's price history.
            Obtained through a call to yf.download
        Returns a QTableWidgetItem with the new performance icon
    """
    # initializes new table widget item and gets the ticker's open, last close, and current prices

    CWD = os.getcwd() + '\\'

    ticker_open = data[1]
    ticker_current = data[0]
    last_close = data[2]

    # calculates the percent change in price from open and from yesterday's close
    open_change = (ticker_current - ticker_open) / ticker_open * 100
    close_change = (ticker_current - last_close) / last_close * 100

    # decides if the stock is up, down, or flat compared to open and yesterday's close
    open_pos = "UP"
    close_pos = "UP"
    if open_change < -.1:
        open_pos = "DOWN"

    elif -.1 < open_change < .1:
        open_pos = "FLAT"

    if close_change < -.1:
        close_pos = "DOWN"
    elif -.1 < close_change < .1:
        close_pos = "FLAT"

    match open_pos:
        case "UP":
            match close_pos:
                case "UP":
                    return QIcon(f"{CWD}icons/greenarrowgreenbox.png")
                case "FLAT":
                    return QIcon(f"{CWD}icons/greenarrowflatbox.png")
                case "DOWN":
                    return QIcon(f"{CWD}icons/greenarrowredbox.png")

        case "FLAT":
            match close_pos:
                case "UP":
                    return QIcon(f"{CWD}icons/flatarrowgreenbox.png")
                case "FLAT":
                    return QIcon(f"{CWD}icons/flatarrowflatbox.png")
                case "DOWN":
                    return QIcon(f"{CWD}icons/flatarrowredbox.png")

        case "DOWN":
            match close_pos:
                case "UP":
                    return QIcon(f"{CWD}icons/redarrowgreenbox.png")
                case "FLAT":
                    return QIcon(f"{CWD}icons/redarrowflatbox.png")
                case "DOWN":
                    return QIcon(f"{CWD}icons/redarrowredbox.png")