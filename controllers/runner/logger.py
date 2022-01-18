import dataclasses
import enum
import logging
import matplotlib.pyplot as plot
import os

NAME = 'online-mnw-robot-learning'


@dataclasses.dataclass
class Settings(logging.Logger):
    """
    Contains the settings for the logger. To guarantee their application, the
    settings have to be committed through the 'setup' function.

    Parameters:
     - path: where to save the log file and the logging plots. Its a folder path
     - log_file: the name of the log file in the path folder
     - log_format: the format of the logging from the application
     - plot_file: the format name of the files containing an matplotlib plotting
     - plot_mode: the modalities of showing, saving, doing both or ignoring the
       plotted graphs.
     - counter: incremental index to not override graphs-plot. It can be changed
    """

    class Mode(enum.Enum):
        """Possible plot-log modalities supported."""

        NONE = 0b00
        SHOW = 0b01
        SAVE = 0b10
        ALL = 0b11

    path: str = ''

    log_file: str = 'log'
    log_format: str = '[%(asctime)s %(levelname)s]\t %(message)s'

    plot_file: str = 'log_plot{idx}.png'
    plot_mode: Mode = Mode.NONE

    counter = 0


def setup(instance: logging.Logger, settings: Settings):
    """
    Define/Set an output file for the logs. The file is specified by the logging
    settings. Moreover, set the logging style/format and the graph-plot
    function.

    :parameter instance: of the logger to set
    :parameter settings: settings to apply to the logger
    """
    logger.plot = lambda plt: log_plot(settings, plt)

    file_path = os.path.join(settings.path, settings.log_file)
    handler = logging.FileHandler(file_path)
    handler.setFormatter(logging.Formatter(settings.log_format))
    instance.addHandler(handler)


def log_plot(settings: Settings, plt: plot):
    """
    Logs a matplotlib plot. The logging follows the configurations specified in
    the 'configuration' parameter and plots the given figure, 'plt'.

    :parameter settings: the settings for the plot
    :parameter plt is the matplotlib plot/figure
    """

    if settings.plot_mode == Settings.Mode.NONE:
        return plt.close()
    elif settings.plot_mode == Settings.Mode.SHOW:
        return plt.show()
    elif settings.plot_mode == Settings.Mode.ALL:
        plt.show()

    plot_name = settings.path + settings.plot_file.format(idx=settings.counter)
    settings.counter += 1
    plt.savefig(plot_name)


logger: logging.Logger = logging.getLogger(NAME)
