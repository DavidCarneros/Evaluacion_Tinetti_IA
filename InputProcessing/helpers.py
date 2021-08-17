import numpy as np
from math import factorial
from constants import Colorama as Color

def peak_detection(data, s=20, max=True):
    """
    Si max = True detecta los máximos
    Si max = False detecta los minimos
    """
    peaks = []
    for i in range(0, len(data)):
        point = data[i]
        pre = True
        post = True
        for j in range(1, s + 1):
            index = i - j
            if index > 0:
                check_p = data[index]
                if max:
                    pre = pre and (point > check_p)
                else:
                    pre = pre and (point < check_p)
            else:
                pre = False
        for j in range(1, s + 1):
            index = i + j
            if index < len(data):
                check_p = data[index]
                if max:
                    post = post and (point > check_p)
                else:
                    post = post and (point < check_p)
            else:
                post = False
        if pre and post:
            peaks.append(i)
    return peaks

def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    """

    """
    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError:
        print(f"{Color.FAIL}[Error] The argument {Color.UNDERLINE}window_size{Color.ENDC} have to be og type int")
        raise ValueError("The argument windows_size have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order+1)
    half_window = (window_size -1) // 2

    b = np.mat([[k ** i for i in order_range] for k in range(-half_window, half_window + 1)])
    m = np.linalg.pinv(b).A[deriv] * rate ** deriv * factorial(deriv)

    firstvals = y[0] - np.abs(y[1:half_window + 1][::-1] - y[0])
    lastvals = y[-1] + np.abs(y[-half_window - 1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve(m[::-1], y, mode='valid')