import matplotlib.pyplot as plt
import numpy as np
from math import floor, ceil

import cfg

plt.style.use("dark_background")

def student_result_line_graph(rollno:int, series:str="", subject:tuple[str, str] = ("000", "Overall")):
    """
    Displays student's result as a line graph

    Parameters
    ----------
    rollno : int
        Roll number of student, used to fetch results
    series : str, optional
        Series to be queried, leave blank to use all
    subject : tuple(str, str), optional
        Subject to display, first element is subject id, second is name
    """

    #Setup matplotlib
    fig, ax = plt.subplots(figsize=(12, 6.75))

    ax.set_title("{} Results".format(subject[1]))
    ax.set_xlabel("Exam ID")
    ax.set_ylim(bottom=0, top=100)
    ax.set_ylabel("Percentage")

    #Fetch data
    try:
        cfg.cur.execute("select distinct results.eid, exams.date, marks_percentage(results.eid, results.sid, results.rollno) from results, exams where exams.eid = results.eid and results.sid='{0}' and results.rollno={1} order by exams.date".format(subject[0], rollno)) #type: ignore
        fetch_data:list[tuple[str, date, float]] = cfg.cur.fetchall() #type:ignore
        len_data = len(fetch_data)

        if len_data == 0:
            cfg.failure("No results found")
            raise
    except:
        cfg.failure("Could not display results")
        return

    index_range = range(len_data)
    eid_list = [fetch_data[i][0] for i in index_range]
    percent_list = [100 * fetch_data[i][2] for i in index_range]
    ax.plot(eid_list, percent_list, 'o-') 

    for i in index_range:
        ax.annotate("{:.2f}%".format(percent_list[i]), (i, percent_list[i]), textcoords="offset points", xytext=(2, 10), ha="center")

    plt.show()


def student_result_frequency_plot(rollno:int, series:str="", subject:tuple[str, str] = ("000", "Overall")):
    """
    Displays student's result as a frequency plot   

    Parameters
    ----------
    rollno : int
        Roll number of student, used to fetch results
    series : str, optional
        Series to be queried, leave blank to use all
    subject : tuple(str, str), optional
        Subject to display, first element is subject id, second is name
    """

    #Setup matplotlib
    fig, ax = plt.subplots(figsize=(12, 6.75))

    ax.set_title("{} Results".format(subject[1]))
    ax.set_xlabel("Percentage")
    ax.set_ylabel("Frequency")


    #Fetch data
    try:
        if series == "":
            cfg.cur.execute("select marks_percentage(eid, sid, rollno) from results where rollno={} and sid='{}'".format(rollno, subject[0]))
        else:
            cfg.cur.execute("select marks_percentage(results.eid, results.sid, rollno) from results, exams where rollno={} and results.sid='{}' and results.eid=exams.eid and exams.series_id='{}'".format(rollno, subject[0], series))
        fetch_data:list[tuple[float]] = cfg.cur.fetchall() #type:ignore
        len_data = len(fetch_data)

        if len_data == 0:
            cfg.failure("No results found")
            raise
    except:
        cfg.failure("Could not display results")
        return
    
    percent_list = [100 * fetch_data[i][0] for i in range(len(fetch_data))]

    histo_gap = 2.5

    lower = floor(min(percent_list) / histo_gap) * histo_gap
    upper = ceil(max(percent_list) / histo_gap) * histo_gap

    bins = np.arange(lower, upper+histo_gap, histo_gap)

    ax.hist(percent_list, edgecolor="#00875f", linewidth=2, bins=bins) #type: ignore

    plt.show()


def student_result_distribution(rollno:int, series:str="", subject:tuple[str, str] = ("000", "Overall")):
    """
    Displays a gaussian probability distribution of the student's marks

    Parameters
    ----------
    rollno : int
        Roll number of student, used to fetch results
    series : str, optional
        Series to be queried, leave blank to use all
    subject : tuple(str, str), optional
        Subject to display, first element is subject id, second is name
    """

    #Setup matplotlib
    fig, ax = plt.subplots(figsize=(12, 6.75))

    ax.set_title("{} Results".format(subject[1]))
    ax.set_xlabel("Percentage")
    ax.set_ylabel("Probability Density")


    #Fetch data
    try:
        if series == "":
            cfg.cur.execute("select marks_percentage(eid, sid, rollno) from results where rollno={} and sid='{}'".format(rollno, subject[0]))
        else:
            cfg.cur.execute("select marks_percentage(results.eid, results.sid, rollno) from results, exams where rollno={} and results.sid='{}' and results.eid=exams.eid and exams.series_id='{}'".format(rollno, subject[0], series))        
        fetch_data:list[tuple[float]] = cfg.cur.fetchall() #type:ignore
        len_data = len(fetch_data)

        if len_data == 0:
            cfg.failure("No results found")
            raise
    except Exception as e:
        cfg.failure("Could not display results")
        cfg.debug(str(e))
        return
    
    percent_list = [100 * fetch_data[i][0] for i in range(len(fetch_data))]

    mean = np.mean(percent_list)
    std = np.std(percent_list)

    lower = max(mean - 4*std, 0)    #type: ignore
    upper = min(mean + 4*std, 100)  #type: ignore
    gauss = np.frompyfunc(lambda x: np.exp(-0.5 * np.square((x - mean) / std)) / (std * np.sqrt(2 * np.pi)), 1, 1)

    x = np.linspace(lower, upper, num=100)


    ax.plot(x, gauss(x), color="#0087ff")

    ax.plot(percent_list, gauss(percent_list), "wo")

    ax.plot([mean, mean], [0, gauss(mean)], color="white")


    shades = 3
    x_shade = [np.array(np.linspace(mean - i * std, mean + i * std, num=100), dtype=float) for i in range(1, shades + 1)]
    y_shade = np.array(gauss(x_shade), dtype=float)
    [ax.fill_between(x_shade[i], y_shade[i], alpha=0.2) for i in range(shades)]

    ax.text(float(mean + 2*std), gauss(mean), "Mean: {:.2f}%".format(mean))
    ax.text(float(mean + 2*std), gauss(mean) * 0.9, "Standard Deviation: {:.2f}%".format(std))

    ax.set_ylim(bottom=0, top = gauss(mean) * 1.2)
    plt.show()