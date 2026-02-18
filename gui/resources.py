"""
Resource management module for Hardware Masquerade GUI
Provides icons, styles, and resource loading functionality
"""

import os
import sys
import base64
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPalette, QFont, QLinearGradient
from PyQt6.QtCore import Qt, QByteArray, QBuffer, QIODevice
from PyQt6.QtWidgets import QStyle, QApplication

class ResourceIcons:
    """Icon resources as base64 strings"""
    
    # Main application icon (32x32)
    APP_ICON = """
    iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAPpSURBVFiF7ZdvaFNnGMZ/7zknTZu0aW3TmlabWl3bKVZxW9dRd7G4iVOdM30Z4kS3D9s+OGQTQfzD+iGIIMwwg/rFwZSBK6hTZOi6wj7MibjVam1t/7S2TZOaf7E1SW1tY3pOTvaBxFhqmpycI/T+4vByzvu8z/vnfe77nPc9gv8J0ul0qVRKBEgkEoIgCJ7B9+HhYfL5PBMTE0QiEd5//30URWF9fZ10Os369etZWlriwYMHFItFwuEwPp+PbDZLLpejv78fr9dLMBgEYHZ2lunpaQYGBggEAuRyOaanp2lqasLn8zE5Ocn09DQHDx5k//79lEolwuEwkiSxuLjIwsICu3bt4uTJk9TU1BAKhZBlmUwmQzKZ5MCBAxw7doxAIMAbb7zBs2fPGB0dpa+vj2w2y61bt3jw4AHbt28nm82yceNGstksmzdvZvPmzYiiiMvlIhQKoSgKkUiEpaUlZmdn6e3tRZZlotEoMzMzHDp0iL1791IsFonH41RXVzM3N0c8Hqevr49IJEI2m6WlpYVwOMzY2Bi9vb10d3dTV1fH3NwciUQCSZJ48cUXicViZLNZRFFk8+bNbN26lVgsRqlUIpFIUF1dzfT0NDdu3KBYLPLVV18Ri8UwTZNkMsnKygpNTU2sW7eOUqlENBqlpaWFUqlEIBDAMAw6Ozupr6+npaWF48ePU1dXx4cffkggEGBkZITdu3dz6dIlNE1j48aNfP/991RVVdHb28s777xDOBzm008/5ebNmzQ1NdHY2Eg+n8c0TRobG2lqakJVVVKpFKqqUldXRyQSoa+vj4aGBr7//nvu3LnD7t272b9/Pzdu3ODGjRu0trZSW1vLhQsXkGWZWCzGzZs3uX37NtXV1Zw8eZILFy4wODjIpUuXOH36NJcuXeLw4cM4HA4aGxux2+3ouo6maQwPD/P1119TVVXF8PAwLpeLjo4Ojh8/znvvvUdnZyder5e+vj5mZmY4dOgQ4+Pj7Nq1i/n5eVRVpbm5mXv37uF0Ojl16hRdXV309vayatUq6uvrMQwDl8tFMplkZGQEn89HMpnE6XTi8/kYGhrC7XYTi8W4desWNTU1eL1eYrEYiUSCYrFIfX09wWCQdDrN+vo6FRUVZDIZ7t+/TzAYZG1tjWw2y5o1a2hra8MwDDo6OjBNk/b2dmKxGIqisLq6iqZp7Nq1i2AwyNraGjabjZqaGhz/r59mZ2eRJAlZlnn06BGhUIhMJoNpmni9XlwuF6urq1gsFhobGykUCqRSKVZWVggGgySTSZaXl6mqqsLn82EYBqlUinw+jyRJpFIpEokENpsNWZZ5/PgxTqeT5eVlUqkUhmHQ0NCAYRisra3h8/lwOBxkMhny+TwOhwO/34+mabjdbkqlEolEglQqRV1dHdXV1aTTadLpNPX19ciyTDqdJp1Os3nzZgRBwDRNDMMgmUyiaRo1NTVYLBZW/7P1DwO8AEZHR0VRFMVgMCiKoigGg0FRFEUxEAiI+XxeNE1TzOfzYj6fF1Op1D8+85+iqip+v59UKoUsywQCAdxuN+l0mmQySTweR9M0/H4/mqaRTCZJpVJkMhk8Hg+ZTIZ0Os26desoFoskk0lM08Tn8+F2u0mn0+i6jtvtpqKigkKhQC6XQ9M0vF4vuq6TTqcxTRNVVfF6vRiGQSqVolgs4nQ68Xg8pNNpNE2joqICj8eDbvz3gP8P+B+GYRjGfxr/AFdEeKq8bYl7AAAAAElFTkSuQmCC
    """
    
    # CPU icon (24x24)
    CPU_ICON = """
    iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAAbFJREFUSIntlbFLw0AUh7+kpdJKhSJdHBz8A9yUXRz6BwiCdRA6uQl26CgIuru5iIu7mx0cxMXJoZOLg5t/QQcHcRO0rVgxVfPS5JKW5Jpz7nvn+/juXe4F/sSBndT6NwCMnH9jx7V+BlBOc2I4KjYH5oEB4Dnn/AFYDvbwJN/xmQDnwFPG+RzwmPKePug6IBN4B1YyzpeZz1y3FbUJwF50HdA3eAEOjfNWT3vI58B4aJk0eAGOjPNmT3vI4wXzbchP35V1/olRfLwzBVaM82ZPe8jHi3kCfq3z74zyAVgy5iRzTQHnjPNmT3vIx4uZ9j0Am0AEXE1gI8PcCOBNLvcEPBvnzZ72kI8XcwP4NM4LwG2W+eT+AzwZ583zHvLxYh4Aj8Z5GbgD3hO4F5L0I8rHa0vei5K0KeXjtaV0KknSW6ScV+O8AtzJdYNYH0C19/3Wdd3AcRy/67pBURTB5uZm2Nv+nOeFpmkGpmlSFAV5ngeDwQDDMLBtG9u2MQwD3/fJ8xzf9ymKAsdxUEpRFAVpmuK6Lkop8jzHcRwcxyHPc5IkQSmF53nkeU6SJCilUEqRZRlJkqCUQmtNlmWkaYpSCq01aZqSpilKKbTWpGlKmqYopdBak6Yp/8kfFJhYi6R70EwAAAAASUVORK5CYII=
    """
    
    # RAM icon (24x24)
    RAM_ICON = """
    iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAAPFJREFUSInt1b9KQ0EQhfFfLggKooWt+BBCwMYXsLWws7QULCx8ARsR36Ctj1DwCSy1E0IeQTtBW1vBkghCLpPNzebmbiHk6wZ2Zr47Z8/OskX8i42q6ZkRMBv5F4C2lCbgGngEHoHPqD8AHmK8AFvAHnhI8H3kuxnzU8AJcAO8A9uS/R3wO+ZnwCbwrCLeBpYB3Wv4XlXyNuY1G+cM+AB2RnjL9yzM6zXOMfABjL94F4CDhHndxjmG8z/gGxi2UfWnS/qL8zeAdRvzOo1zAOev6dWrF3gA3hLmdRvnIOZ31QO8AaPAV8J6W8Z5q3qAB+A54T1Lmeet6gH6P7oHdHpUYf4WvokAAAAASUVORK5CYII=
    """
    
    # Disk icon (24x24)
    DISK_ICON = """
    iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAAMZJREFUSIntlL0NAUEQhb9tSqAFJSgBiWgCJSpQgUb8lEBE1ECrBGUoQQlKUIJEgrgL2diZs7u3A9/eZvbN5M3sW4R/KZRSRZZlNq11VZblWAiB1hpjzFhrXddorbHWjnmeY4whCAI8z8MYg7UWYwye55EkCcYYgiDA8zxiYiLCGIMxhlVrba1pmobX60Ucx0RRhDGGJEn4fD4Mw4AQAqUUn8+HOI5xXZdlWeYxIiJJEqy1GGNQSgEhURQhIg+stUgpMcYQhiFaa0opjDForZFSIqWc1hARpJQopYjjGGMMUkqEECil+NE6A1WlK8eM5T5iAAAAAElFTkSuQmCC
    """
    
    # MAC icon (24x24)
    MAC_ICON = """
    iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAAUdJREFUSInt1j9Lw0AYBvDn0qUUhYLgIrgU7CaILh2r+A0EB8HV2T5BcRMEZz+Bi+Dm6iC6iFhUUGxLpRJq+ydNk1x6lyYt9IJvyZ3c8zx3vPfeHfzLWpG+a2YGZpZizpG55xhrZkKSLRnmNE2RZRk8z0OSJPA8D1mWQUpJg67rIIRASgmlFCIiCCGQZRk8z0NVVdA0DUopZFkGz/OglEJVVSAiKKUQBAFc10VVVVBKIQgCuK6LMAxRliWUUnBdF0opRFEEpRTCMITrulBKIY5jRFEEx3FgjEEcR4jjGLZtQwjRwUIIWJaFIAiQJAls20ZVVUjTFLZtIwgClGUJ27YxHo+hlEJZlhiPx9A0DWVZIkkSjEYjMMYQxzGSJIHneSCiDq6UAiEE4jiG4zhgjKFpGqRpCiEEiAiapkHTNBARwjCE53lomoZfFgA/OBgOh5/eZwcjdjMAAAAASUVORK5CYII=
    """
    
    # GPU icon (24x24)
    GPU_ICON = """
    iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAAU9JREFUSInt1b9KQ0EQx/HPhUAKCxFsREjADnyF+AKJCr4AImKlbyIomCJgYyWmSmVnZWst2KURIwTxH3hCrpA9OIfHXW5zwZwf2N3Z+bIzuztbxH+0kWU+Xk9sW0KIZVteSindEUJwXVdrmqbJMAwMw0Cv10vTNBJC0DgOY4x5XddVURRSa03TNDJNE8YYmqbJMIxpmqYoioI0TeM4Tl3Xpa7rGMcxWZZRVRV1XRPHMVmWkWWZ2qYQAmMMnufBOSdJEnDOwRjDNE3CGCcMw1nDMAiCgLqu4XkePM8jSRJIkuA4jqwoClBKjRlj8H0fvu8jTdPOd9d1aZoGSZKAcw7LsiClhOd5sCwLmqahKAqmaQrLstA0DcuyoGkaRVFQVRUsy4JhGERRRFVV4JzDMAyqqoJlWVAUhSRJoGkaFEWBEAJpmmCaBkVRkOc5hBBI0xRZlkFKKYIgQJ7nEEJASgkhBKIogqIoEEJA13WkaQohBIQQkFJCSglN0yCEgJQSmqZBCAHP8yClhKZpEELA8zxIKaFpGoQQ8DwPUkpomoYQQkgp8T/zC8S0XXopbQ9PAAAAAElFTkSuQmCC
    """
    
    # Motherboard icon (24x24)
    MOTHERBOARD_ICON = """
    iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAAV5JREFUSInt1b9LQlEcxfFPSwQ1BEFLEARtDTU1tERLf4FDbYk0RBBtLRJBLYIQFNGWSE6iSEtEg9TU1hIEbS0hBP2BvFh83Hf1eb1FyH7D2T33fO7hnu+9j4h/YcZGon0CEJG9IuKb5iIiiqKQMAxDF4uiKPj9/lBExDRN4jgO2+12wzRNBEEQ+r5PkiQEQRD6vk+SJPh9H9/38X2fMAzxPA/LssiyjDAM8X0fz/MQEZxzgiDAcRysdQjnHM45giBARMjzHOccpZRSSnEcx3Ecq5RSRVFQFAW11lRKCWMMpRQRwVqLUkprrZVSFEVBmqY0TdM0TfM8J8syWmu11iIiWGuVUqIoCpqmKaWUUEqplKJpmlJKaa1prdVaCyGklBJCiCAIhFJKCCFKKZVSIoQQpZQQQpRSSgghSgkhhFJKCKVUjDHGGMYYY4wxxhhjjDHGGGOMMcYYY4zFGGOMMcYYY4zFGGOMMcYYY4zFGGOMMcYYY4yxGGMs/r/4AjxPQpOuxD1iAAAAAElFTkSuQmCC
    """
    
    # BIOS icon (24x24)
    BIOS_ICON = """
    iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAANpJREFUSInt1b9LQlEYgPHvOVyEIIKgqKmh0N+gqS1aWhqaIiIImhoa+g+CpqKIP0JTQ0tNS0tLQ0u0BIGg3+C98N7Dvfd8Fw+8bzvPec7zcs77vgj/WtG2c1mWHkVR2oqiKD0Mw3QVkQsiZ0TkIzI0TROl1NiyLMqyZG0sl2mapFIKpRSWZZGmKb7vI5IxHo9J0xRjDFprRKRiGAZRFKGUYjAYMJ/P0VojIhVKKQaDAVEUobVGRCqUUsRxTJqmaK0RkQqlFHEcM5vN0FojIhVKKUzTZD6fo7VGRCq01iilME2TMAzRWlMUBcYYlFJorRFCsCwLpRRBEGCMwTAMhBDCMCQMwylrLUEQYJomWmuEECzLQghBa00QBGitaa0JggCtNa01QRCgtaa1RghBa40QQhAE/J8vYypnP+tMgtwAAAAASUVORK5CYII=
    """
    
    # Monitor icon (24x24)
    MONITOR_ICON = """
    iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAAMFJREFUSInt1cFKA0EMBuAvpS4KgoiCB1/Bi+ALiPge3n0FQdCbF5/Fi+BFEESKqK2yG3dGht3ZObM7B/d8yZ8h+bMk0xH+YqlKz5nMvWmeKq3Xg+u6TCaT6LquaZqm1nVdaZomhmGQZZnkeU4YhlIUBWma0nUdWZZJURSEYUgYhpRlSVEUhGFIURRYa2maBsdxyLIMay2u6+I4Dq7rYq3FdV2stbiui7UWYwzWWowxWGvRWmOtRWuNtRZjjLUWYwzWWowxWGsRkVH8D24Bmhgn8fL/AAAAAElFTkSuQmCC
    """
    
    # Play/Start icon (24x24)
    PLAY_ICON = """
    iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAAL5JREFUSInt1T9LAnEcwPH3FxCU4O7g5OBkU5Bz7+AtuLs6BcHN0ckH4EtwcHEQnOzuIjQXH5A9g3sIL4iDn0p/7hvuO93wuL4+w/cHnzv4IgRjjDHGGGOMMf+3yWSCEAJrLcYYWmu01gRBwH6/h4jGGPZ7hBAcDgcIIYQQTKdT6vU6m80Gay3VapVqtUoYhmit6fV61Go1tNZ0u11KpRJaazqdDkopZrMZjuNQKBTQWpMkCVEUkc/n0VqTpz6dTqlUKuR5Tp7nVCoV8vR+v0eWZeTp/X7/zR8+AZJ2I3vSq+EXAAAAAElFTkSuQmCC
    """
    
    # Stop icon (24x24)
    STOP_ICON = """
    iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAAH1JREFUSInt1bEJw0AMheFPA9kik9kO2yTbZIuskVUyQmqTGTyFp0u5EC4h3XvfX6BBAwYMGDDg3x2PByEEnHMYY0iSBCEEzjmEEBhj6LqOvu+JoggpJdZa0jTFWktd17iuS9d19H1PnudYa0nTlLIs6bqOpmnIsoy+7ynLkq7r+C2fF6JuM71pFdNvAAAAAElFTkSuQmCC
    """
    
    # Refresh icon (24x24)
    REFRESH_ICON = """
    iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAAm9JREFUSInt1T1oFUEQB/Df3QdJIIqIhUVAgooYhYgKQbGwUxArQURQ0M7GRiwEUwj2ImJhZSFW/oVOREEU1EKBmCJFxKAgKChChFhYKIpEEh/7Jjz2mBv2vfveS0B/wy47O7e/PbM7swv/M1ljayWwE1gPzANbgRXAb8dj6k4EQUT2iEi7iLSLSIeItIuIisg1EZkSkdci8lZE3opIRkTGReSdiPwwr18TkR8i8l1EciIyISKfROSViLyPqhWRCyLyUURyIvLJvD4XVS8iF0VkXERyIpIxr8+LSD7KJ2Ze/xKREvP6WER+ikjR7D2b15+ISAW4X3n2H/JBRD6JSMG8LpjXH1W+/X0RmbLePxCRQlR9pIqH5vWniDx0AbAq4iE9WnUQER4R4RERHhHhERFOz2+32+12u91u98Zsb29n3759bGpqYvfu3Wxububx48c5NzfH5eVlLi8vs9Vq4dSpUxwdHcUYgzEGYwzGGIwxGGMwxmCMwRiDMQZjDMYYjDEYYzDGYIzBGIMxBmMMxhiMMRhjMMZgjMEYgzEGYwzGGIwxGGMwxmCMwRiDMQZjDMYYjDEYYzDGYIzBGIMxBmMMxhiMMRhjMMZgjMEYgzEGYwzGGIwxGGMwxmCMwRiDMQZjDMYYjDEYYzDGYIzBGIMxBmMMxhiMMRhjMMZgjMEYgzEGYwzGGIwxGGMwxmCMwRiDMQZjDMYYjDEYYzDGYIzBGIMxBmMMxhiMMRhjMMZgjMEYgzEGYwzGGIwxGGMwxmCMwRiDMQZjDMYYjDEYYzDGYIzBGIMxBmMMxhiMMRhjMMZgjMEYgzEGYwzGGIwxGGMwxmCMwRiDMQZjDMYYjDEYYzDGYIzBGIMxBmMMxhiMMRhjMMZgjMEYgzEGYwzGGIwxGGMwxmCMwRiDMQZjDMYYjDEYYzDGYPyN+QeQy/tZ8F8D6gAAAABJRU5ErkJggg==
    """
    
    # Checkmark icon (24x24)
    CHECK_ICON = """
    iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAAXVJREFUSInt1b9LQmEUxvHv0R+iKag/oIi2oBbBNRpqamgLWhoaov6BioY+EA0NQURDbQ1RLS3R0iI01BY0tAT9Ad6LcJF37/V674W+8CwHzvvwnHPeV/iX0uQKbQH7QB+oAq/AAzAC3oFlYBo4SgsOCwhEpF9EciLyHBERkbyI5EREiUhBREoiUhYRKYlIRUSWgR6wDVSAK6AfaAMj4AE4BnbD4r8vjIF14EUtYwN4VJ+x4r0/BZ6i6v2fAb14f3gT2K2I/NRntUfiPXCnJgGcw1O0tQWU4/3hG0AN2FeTANZgGm1tADm4j6r3fwY4iPdHrQGPwEe0tQVsq0kA6/CjJgE0oxz4m1kGjqLq/Z8BvMb7o6oAD2oTQHX4UpMA2uFHTQLoRTnwP7N6mEW7ANdAHTiMqvd/BniJ90d1AT7VJoB++FWTABbhR30f4Fb9NysA52p+Z34B9oAptQlgG6hE+Q3gJd4f/jVgDlhRmwB6wI2aBHALPKhJALfAg5oEcAs8qEkAt8CDmgRwCzyoSQC3wIP+B4F/Jp8XjQp1zWYAAAAASUVORK5CYII=
    """
    
    # Error icon (24x24)
    ERROR_ICON = """
    iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAAn9JREFUSInt1U2ITnEYx/HPmReyEQphI8rCghRlM1EUY2GjkFhQkqRYKYqUJCs7K4oNsmDBS1YspJSNiYXJKCkLWZA3C0a8NOP/zI1r7tzzPDN1J3+b5+Z6nud3n3Oe7//7X8R/lI6ODnV3d2t8fFzj4+MaHx/X2NiY2tvbBQBqa2tTa2urZmZm1NfXp7m5OQEQYwwxxhBjjDHGEEIIIYYYYogxhhhjjDHGEEIIIYYYYogxhhhjjDHGEEIIIYYYYogxhhhjjDHGEEIIIYYYYogxhhhjjDHGEEIIIYYYYogxhhhjjDHGEEIIIYYYYogxhhhjjDHGEEIIIYYYYogxhhhjjDHGEEIIIYYYYogxhhhjjDHGEEIIIYYYYogxhhhjjDHGEEIIIYYYYogxhhhjjDHGEEIIIYYYYogxhhhjjDHGEEIIIYYYYogxhhhjjDHGEEIIIYYYYogxhhhjjDHGEEIIIYYYYogxhhhjjDHGEEIIIYYYYogxhhhjjDHGEEIIIYYYYogxhhhjjDHGEEIIIYYYYogxhhhjjDHGEEIIIYYYYogxhhhjjDHGEEIIIYb/hGq1iq6uLpSXl2Pbtm1obm7G4cOHMTk5iZ6eHpw+fRrT09MYGBhAaWkpOjs70dvbCwBIpVIoLy9HJpOBiGB8fBwTExM4cOAAWltb0dLSgqNHj2JwcBDT09M4deoUTp48iT179uDChQu4du0aVq5ciSNHjuDOnTsAgGQyid27dyOTyWBqagrpdBpnz57FhQsXsHv3bpw/fx7pdBo3b97E5cuXcfz4cVy6dAn37t3DmzdvsG3bNqRSKQwMDKCnpyf4++fPn6O6uhoNDQ2YnJwM/p9IJDA4OIh4PI7h4WEsWbIEw8PDmJycRG1tLTo6OgJ9W1sb6urq0Nraivr6ejQ2NmJiYgLLli1DQ0MDGhoaUFdXh7a2Nnz9+hW7du3Chg0b0Nraim/fvmFoaAhr1qxBPB7H2NgY2tvbEYvFkEgk0Nvbiw8fPqCiogLr169He3s7vn79ivb2dqxfvx7pdBoff3wE/wYAmxiCv4Dx1pUAAAAASUVORK5CYII=
    """
    
    # Success icon (24x24)
    SUCCESS_ICON = """
    iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAAi9JREFUSInt1UtoU0EQBuB/T0k1iYoarSBa86i1glRBUUQjIh5sRS0qHhT16EUpghcR9aB4K4oXiyLoRcWDJ1u8tYr4qFhBqxZEFHwE8YFta0FBtT77kI4w6b03741pCz0wLOzOzj87szszh/85WRYyDuP4BHE8hjiOII4jEeMUiPEEiHEaxDgTYpwNMc6BGGdBjOMgxnEQ4ziIcRzEOA5iHAcxjoMYx0GM4yDGcRDjOIhxHMQ4DmIcBzGOgxjHQYzjIMZxEOM4iHEcxDgOYhwHMY6DGMdBjOMgxnEQ4ziIcRzEOA5iHAcxjoMYx0GM4yDGcRDjOIhxHMQ4DmIcBzGOgxjHQYzjIMZxEOM4iHEcxDgOYhwHMY6DGMdBjOMgxnEQ4ziIcRzEOA5iHAcxjoMYx0GM4yDGcRgZpk+fpvPnKZ1O0+nTp+n06dN0+vRpunDhAi1cuJCOHj1Kq1aton379tHr169p+fLl1NvbS1u3bqW1a9dSX18f9fb2Ul9fH+VyOZqYmKBcLkfbtm2jrq4u2rx5M2UyGdqzZw9lMhnKZrOUz+dpcnKS8vk8HTx4kNra2qi1tZVyuRxNTEzQ2NgYFYtF6u/vp5aWFmppaaG+vj4aHx+nsbExmjdvHrW3t1NfXx8NDQ1RsVik+vp6WrBgARWLRRoYGKBisUjz58+n5uZmKhaL1N/fT8VikebOnUuzZ8+mv5X/B16pVOjz58/0+fNn+vLlC3358oU+f/5MxWKRisUiFYtFKhQK9OPHDyoUClQsFqlQKNDs2bPp9+/f9OvXL5o9ezb9+vWLfv78Sb9+/aJZs2bR9+/f6cePHzRr1iyqVCr048cP+vnzJ1UqFZoxYwZVKhX68eMH/fr1i2bMmEGVSoUqlQrV1NQ89vkF8LpMg/vsh7sAAAAASUVORK5CYII=
    """
    
    # Settings icon (24x24)
    SETTINGS_ICON = """
    iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAApBJREFUSInt1U2IjlEcx/HPjBezYMMLpWwaY0FqZqG8LM3SghoLe9lQykJZKGZBUiiFlCyyYqEUk5Ss2FhQs2KlMdtR3goyG+b/f7rP/Tz3M/eZZ5h8/OvW/Zz7d73O/3fO/5z/Ef9RtVqNtrY2NDU1Yd68edi2bRvOnz+PW7duYd++fTh16hSuXLmCpUuXYuvWrdi+fTsA4O3bt2hsbER9fT3WrFmD169fo7+/H4lEAu3t7WhtbcWpU6ewf/9+XgYHBwEAZ86cwY4dO3D9+nW8evUKfX19AIBkMonly5fj6NGj6O/vR1dXF3p7ezEwMIBYLIZ0Oo0XL15gYGAAqVQK+XweBw4cQDqdRj6fRzweRzKZxMuXL9Hb24tEIoGBgQFcvXoV3d3duH79Ojo7O1Eul1EqlXjJ5XI4efIkersH0dvbjWw2i2w2i0KhgN7eHmSzWeRyOTx48ABv375FsVhEoVBAJpPBu3fvcP/+fTQ0NOD8+fPI5/PI5/N49OgR7t69i46ODjx58gS5XA65XA7ZbBaPHz/G7du30dHRgWw2i2w2i1wuhydPnuDWrVvo7OxEJpNBLpdDLpdDLpfD06dPcfPmTXR1dSGbzSKXyyGXyyGfz+PZs2e4ceMGuru7kc1mkclkkM/nkU6n8fz5c1y/fh09PT1ob29HOp1GJpNBLpdDoVDAixcvcO3aNfT29iKdTiOTyWBkZATDw8N4+fIlrl69iv7+frS3tyOdTqNUKqFUKuHVq1e4cuUK+vv70d7ejlQqhVKphFKphNevX+Py5csYGBhAOi1vUqlUyv3lyxdcunQJAwMDaG9vRyqVQqVSwZs3b/Dy5UsMDAygvb0d/f39qFQqqFQqePv2LV68eIFMJpPx+QeMv6rykf6iUwAAAABJRU5ErkJggg==
    """


class ResourceStyles:
    """Stylesheet resources"""
    
    # Main window style
    MAIN_STYLE = """
    QMainWindow {
        background-color: #2b2b2b;
    }
    
    QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 10pt;
    }
    
    QLabel {
        color: #ffffff;
        background-color: transparent;
        padding: 2px;
    }
    
    QLabel#title_label {
        font-size: 18pt;
        font-weight: bold;
        color: #4CAF50;
        padding: 10px;
    }
    
    QLabel#subtitle_label {
        font-size: 11pt;
        color: #cccccc;
        padding: 5px;
    }
    
    QLabel#status_label {
        font-size: 10pt;
        color: #ffaa00;
        padding: 5px;
        border: 1px solid #3c3c3c;
        border-radius: 3px;
        background-color: #333333;
    }
    
    QPushButton {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 10pt;
    }
    
    QPushButton:hover {
        background-color: #45a049;
    }
    
    QPushButton:pressed {
        background-color: #3d8b40;
    }
    
    QPushButton:disabled {
        background-color: #555555;
        color: #888888;
    }
    
    QPushButton#danger_button {
        background-color: #f44336;
    }
    
    QPushButton#danger_button:hover {
        background-color: #da190b;
    }
    
    QPushButton#warning_button {
        background-color: #ff9800;
    }
    
    QPushButton#warning_button:hover {
        background-color: #e68900;
    }
    
    QGroupBox {
        border: 2px solid #3c3c3c;
        border-radius: 5px;
        margin-top: 1ex;
        padding-top: 10px;
        font-weight: bold;
        color: #4CAF50;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 10px;
        padding: 0 5px 0 5px;
    }
    
    QListWidget {
        background-color: #333333;
        border: 1px solid #3c3c3c;
        border-radius: 3px;
        color: #ffffff;
        outline: none;
    }
    
    QListWidget::item {
        padding: 5px;
        border-bottom: 1px solid #3c3c3c;
    }
    
    QListWidget::item:selected {
        background-color: #4CAF50;
        color: white;
    }
    
    QListWidget::item:hover {
        background-color: #404040;
    }
    
    QTabWidget::pane {
        border: 1px solid #3c3c3c;
        border-radius: 5px;
        background-color: #2b2b2b;
    }
    
    QTabBar::tab {
        background-color: #333333;
        color: #ffffff;
        border: 1px solid #3c3c3c;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        padding: 8px 16px;
        margin-right: 2px;
    }
    
    QTabBar::tab:selected {
        background-color: #4CAF50;
        color: white;
    }
    
    QTabBar::tab:hover:!selected {
        background-color: #404040;
    }
    
    QMenuBar {
        background-color: #333333;
        color: #ffffff;
        border-bottom: 1px solid #3c3c3c;
    }
    
    QMenuBar::item {
        background-color: transparent;
        padding: 4px 10px;
    }
    
    QMenuBar::item:selected {
        background-color: #4CAF50;
        color: white;
        border-radius: 3px;
    }
    
    QMenu {
        background-color: #333333;
        color: #ffffff;
        border: 1px solid #3c3c3c;
        border-radius: 3px;
    }
    
    QMenu::item {
        padding: 5px 20px;
    }
    
    QMenu::item:selected {
        background-color: #4CAF50;
        color: white;
    }
    
    QMenu::separator {
        height: 1px;
        background-color: #3c3c3c;
        margin: 5px 0;
    }
    
    QCheckBox {
        color: #ffffff;
        spacing: 8px;
    }
    
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border-radius: 3px;
        border: 1px solid #3c3c3c;
        background-color: #333333;
    }
    
    QCheckBox::indicator:checked {
        background-color: #4CAF50;
        border-color: #4CAF50;
    }
    
    QCheckBox::indicator:hover {
        border-color: #4CAF50;
    }
    
    QRadioButton {
        color: #ffffff;
        spacing: 8px;
    }
    
    QRadioButton::indicator {
        width: 16px;
        height: 16px;
        border-radius: 8px;
        border: 1px solid #3c3c3c;
        background-color: #333333;
    }
    
    QRadioButton::indicator:checked {
        background-color: #4CAF50;
        border-color: #4CAF50;
    }
    
    QRadioButton::indicator:hover {
        border-color: #4CAF50;
    }
    
    QComboBox {
        background-color: #333333;
        color: #ffffff;
        border: 1px solid #3c3c3c;
        border-radius: 3px;
        padding: 5px;
        min-height: 20px;
    }
    
    QComboBox:hover {
        border-color: #4CAF50;
    }
    
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
        border-left: 1px solid #3c3c3c;
    }
    
    QComboBox QAbstractItemView {
        background-color: #333333;
        color: #ffffff;
        border: 1px solid #3c3c3c;
        selection-background-color: #4CAF50;
    }
    
    QLineEdit {
        background-color: #333333;
        color: #ffffff;
        border: 1px solid #3c3c3c;
        border-radius: 3px;
        padding: 5px;
    }
    
    QLineEdit:focus {
        border-color: #4CAF50;
    }
    
    QSpinBox {
        background-color: #333333;
        color: #ffffff;
        border: 1px solid #3c3c3c;
        border-radius: 3px;
        padding: 5px;
    }
    
    QSpinBox:focus {
        border-color: #4CAF50;
    }
    
    QStatusBar {
        background-color: #333333;
        color: #ffffff;
        border-top: 1px solid #3c3c3c;
    }
    
    QProgressBar {
        border: 1px solid #3c3c3c;
        border-radius: 3px;
        text-align: center;
        color: white;
    }
    
    QProgressBar::chunk {
        background-color: #4CAF50;
        border-radius: 2px;
    }
    
    QScrollBar:vertical {
        background-color: #333333;
        width: 14px;
        border: none;
        border-radius: 7px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #4CAF50;
        min-height: 20px;
        border-radius: 7px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #45a049;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        border: none;
        background: none;
    }
    """
    
    # Dialog style
    DIALOG_STYLE = """
    QDialog {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    
    QLabel {
        color: #ffffff;
        background-color: transparent;
    }
    
    QPushButton {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 3px;
        min-width: 80px;
    }
    
    QPushButton:hover {
        background-color: #45a049;
    }
    
    QPushButton:pressed {
        background-color: #3d8b40;
    }
    """
    
    # Process list item style for spoofed processes
    SPOOFED_ITEM_STYLE = """
    background-color: #4CAF50;
    color: white;
    font-weight: bold;
    """
    
    # Active spoof indicator
    ACTIVE_SPOOF_STYLE = """
    QLabel {
        color: #4CAF50;
        font-weight: bold;
        font-size: 10pt;
    }
    """
    
    # Warning/Error message style
    WARNING_STYLE = """
    QLabel {
        color: #ff9800;
        font-weight: bold;
    }
    """
    
    ERROR_STYLE = """
    QLabel {
        color: #f44336;
        font-weight: bold;
    }
    """
    
    # Success message style
    SUCCESS_STYLE = """
    QLabel {
        color: #4CAF50;
        font-weight: bold;
    }
    """


class ResourceManager:
    """Resource manager for loading and caching resources"""
    
    _instance = None
    _icons = {}
    _pixmaps = {}
    _fonts = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self._load_base_icons()
    
    def _load_base_icons(self):
        """Load base64 encoded icons"""
        icon_map = {
            'app': ResourceIcons.APP_ICON,
            'cpu': ResourceIcons.CPU_ICON,
            'ram': ResourceIcons.RAM_ICON,
            'disk': ResourceIcons.DISK_ICON,
            'mac': ResourceIcons.MAC_ICON,
            'gpu': ResourceIcons.GPU_ICON,
            'motherboard': ResourceIcons.MOTHERBOARD_ICON,
            'bios': ResourceIcons.BIOS_ICON,
            'monitor': ResourceIcons.MONITOR_ICON,
            'play': ResourceIcons.PLAY_ICON,
            'stop': ResourceIcons.STOP_ICON,
            'refresh': ResourceIcons.REFRESH_ICON,
            'check': ResourceIcons.CHECK_ICON,
            'error': ResourceIcons.ERROR_ICON,
            'success': ResourceIcons.SUCCESS_ICON,
            'settings': ResourceIcons.SETTINGS_ICON,
        }
        
        for name, data in icon_map.items():
            self._icons[name] = self._create_icon_from_base64(data)
    
    def _create_icon_from_base64(self, base64_data):
        """Create QIcon from base64 encoded PNG data"""
        try:
            # Remove whitespace and newlines from base64 string
            clean_data = ''.join(base64_data.split())
            
            # Decode base64 to bytes
            image_data = base64.b64decode(clean_data)
            
            # Create QByteArray from bytes
            byte_array = QByteArray(image_data)
            
            # Create QPixmap from QByteArray
            pixmap = QPixmap()
            pixmap.loadFromData(byte_array)
            
            # Create QIcon from QPixmap
            return QIcon(pixmap)
        except Exception as e:
            print(f"Failed to create icon: {e}")
            return QIcon()
    
    def get_icon(self, name, size=None):
        """Get icon by name, optionally resized"""
        icon = self._icons.get(name)
        if icon and size:
            # Create resized version
            pixmap = icon.pixmap(size)
            return QIcon(pixmap)
        return icon or QIcon()
    
    def get_pixmap(self, name, size=None):
        """Get pixmap by name, optionally resized"""
        if name not in self._pixmaps:
            # Create pixmap from icon
            icon = self.get_icon(name)
            if not icon.isNull():
                self._pixmaps[name] = icon.pixmap(32, 32)
        
        pixmap = self._pixmaps.get(name)
        if pixmap and size:
            return pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, 
                                Qt.TransformationMode.SmoothTransformation)
        return pixmap
    
    def get_font(self, name, point_size=10, weight=QFont.Weight.Normal):
        """Get font by name and properties"""
        font_key = f"{name}_{point_size}_{weight}"
        if font_key not in self._fonts:
            font = QFont(name, point_size)
            font.setWeight(weight)
            self._fonts[font_key] = font
        return self._fonts[font_key]
    
    def get_style(self, style_name):
        """Get stylesheet by name"""
        styles = {
            'main': ResourceStyles.MAIN_STYLE,
            'dialog': ResourceStyles.DIALOG_STYLE,
            'spoofed_item': ResourceStyles.SPOOFED_ITEM_STYLE,
            'active_spoof': ResourceStyles.ACTIVE_SPOOF_STYLE,
            'warning': ResourceStyles.WARNING_STYLE,
            'error': ResourceStyles.ERROR_STYLE,
            'success': ResourceStyles.SUCCESS_STYLE,
        }
        return styles.get(style_name, '')
    
    def apply_style(self, widget, style_name):
        """Apply stylesheet to widget"""
        style = self.get_style(style_name)
        if style:
            widget.setStyleSheet(style)
    
    def get_process_icon(self, process_name):
        """Get appropriate icon for process type"""
        process_lower = process_name.lower()
        
        # Map process names to icons
        if any(x in process_lower for x in ['chrome', 'firefox', 'edge', 'opera', 'browser']):
            return self.get_icon('app', QSize(16, 16))
        elif any(x in process_lower for x in ['game', 'steam', 'epic', 'origin', 'uplay']):
            return self.get_icon('gpu', QSize(16, 16))
        elif any(x in process_lower for x in ['system', 'svchost', 'services']):
            return self.get_icon('cpu', QSize(16, 16))
        elif any(x in process_lower for x in ['explorer']):
            return self.get_icon('disk', QSize(16, 16))
        else:
            return self.get_icon('settings', QSize(16, 16))
    
    def get_status_icon(self, status):
        """Get icon for status"""
        status_map = {
            'success': 'success',
            'error': 'error',
            'warning': 'error',
            'info': 'settings',
            'running': 'play',
            'stopped': 'stop',
            'active': 'check',
        }
        icon_name = status_map.get(status.lower(), 'settings')
        return self.get_icon(icon_name, QSize(16, 16))


# Global resource manager instance
resources = ResourceManager()


def init_resources():
    """Initialize resources (call at application startup)"""
    global resources
    return resources


def get_icon(name, size=None):
    """Convenience function to get icon"""
    return resources.get_icon(name, size)


def get_pixmap(name, size=None):
    """Convenience function to get pixmap"""
    return resources.get_pixmap(name, size)


def get_style(name):
    """Convenience function to get stylesheet"""
    return resources.get_style(name)


def apply_style(widget, name):
    """Convenience function to apply stylesheet"""
    resources.apply_style(widget, name)


# Resource paths for external files (if used)
class ResourcePaths:
    """Paths to external resource files"""
    
    @staticmethod
    def get_base_path():
        """Get base path for resources"""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            return os.path.dirname(sys.executable)
        else:
            # Running as script
            return os.path.dirname(os.path.abspath(__file__))
    
    @staticmethod
    def get_icon_path(icon_name):
        """Get path to icon file"""
        base = ResourcePaths.get_base_path()
        
        # Try different possible locations
        possible_paths = [
            os.path.join(base, 'icons', f'{icon_name}.png'),
            os.path.join(base, 'resources', 'icons', f'{icon_name}.png'),
            os.path.join(base, f'{icon_name}.png'),
            os.path.join(os.path.dirname(base), 'icons', f'{icon_name}.png'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    @staticmethod
    def get_translation_path(lang_code):
        """Get path to translation file"""
        base = ResourcePaths.get_base_path()
        
        possible_paths = [
            os.path.join(base, 'translations', f'{lang_code}.qm'),
            os.path.join(base, 'resources', 'translations', f'{lang_code}.qm'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    @staticmethod
    def get_config_path():
        """Get path to configuration file"""
        base = ResourcePaths.get_base_path()
        return os.path.join(base, 'config.ini')
    
    @staticmethod
    def get_driver_path():
        """Get path to driver file"""
        base = ResourcePaths.get_base_path()
        return os.path.join(base, 'HardwareSpoofer.sys')
    
    @staticmethod
    def get_loader_path():
        """Get path to loader executable"""
        base = ResourcePaths.get_base_path()
        return os.path.join(base, 'loader.exe')


# Example usage in main.py:
"""
from resources import resources, get_icon, get_style, apply_style

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set window icon
        self.setWindowIcon(get_icon('app'))
        
        # Apply main style
        apply_style(self, 'main')
        
        # Create button with icon
        self.btn = QPushButton(get_icon('play'), 'Start')
        
        # Style specific widget
        self.status_label = QLabel()
        apply_style(self.status_label, 'active_spoof')
"""