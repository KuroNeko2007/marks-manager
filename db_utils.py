from datetime import date
import cfg

def check_student_exists(rollno: int) -> bool:
    """
    Checks if particular student is in database

    Parameters
    ----------
    rollno : int
        Roll number of student to search for

    Returns
    -------
    bool
        True if student exists and false otherwise

    Raises
    ------
    mysql.connector.Error
        If query fails for any reason
    """

    cfg.cur.execute("select 1 from students where rollno={} limit 1".format(rollno))

    return len(cfg.cur.fetchall()) != 0


def check_exam_exists(exam_id: str) -> bool:
    """
    Checks if particular exam is in database

    Parameters
    ----------
    exam_id : str
        Exam ID of exam to search for

    Returns
    -------
    bool
        True if exam exists and false otherwise

    Raises
    ------
    mysql.connector.Error
        If query fails for any reason
    """

    cfg.cur.execute("select 1 from exams where eid='{}' limit 1".format(exam_id))

    return len(cfg.cur.fetchall()) != 0


def check_result_exists(rollno: int, exam_id: str) -> bool:
    """
    Checks if particular result is in database

    Parameters
    ----------
    rollno : int
        Roll number of student to search for
    exam_id : str
        Exam ID of exam to search for

    Returns
    -------
    bool
        True if result exists and false otherwise

    Raises
    ------
    mysql.connector.Error
        If query fails for any reason
    """

    cfg.cur.execute("select 1 from results where eid='{}' and rollno={} limit 1".format(exam_id, rollno))

    return len(cfg.cur.fetchall()) != 0



def fetch_sub_max_marks(exam_id: str) -> int|None:
    """
    Fetches maximum marks per subject for a particular exam

    Parameter
    ---------
    exam_id : str
        Exam ID of exam to fetch for

    Returns
    -------
    int
        Maximum marks per subject for particular exam
    None
        If no such exams found in records

    Raises
    ------
    mysql.connector.Error
        If query fails due to any reason 
    """

    cfg.cur.execute("select sub_max_marks from exams where eid='{}'".format(exam_id))

    records:list[tuple[int]] = cfg.cur.fetchall() #type: ignore

    if len(records) == 0:
        return None
    else:
        return records[0][0]

def fetch_subject_name(subject_id: str) -> str|None:
    """
    Fetches name of subject given the subject id

    Parameter
    ---------
    subject_id : str
        Subject ID of subject to fetch for

    Returns
    -------
    str
        Name of subject for specified id
    None
        If no such subjects found in records

    Raises
    ------
    mysql.connector.Error
        If query fails due to any reason
    """

    cfg.cur.execute("select name from subjects where sid='{}'".format(subject_id))

    records: list[tuple[str]] = cfg.cur.fetchall() #type: ignore

    if len(records) == 0:
        return None
    else:
        return records[0][0]




def fetch_exam_list() -> list[tuple[str, str, date, int]]:
    """
    Fetches list of all exams in records, orders by date desc

    Returns
    -------
    list[tuple[str, str, Date, int]]
        List of tuples of exams
        Tuple elements are exam id, series id, date and maximum marks per subject respectively

    Raises
    ------
    mysql.connector.Error
        If the query fails due to any reason
    """

    cfg.cur.execute("select eid, series_id, date, sub_max_marks from exams order by date desc")

    return cfg.cur.fetchall() #type: ignore



def fetch_series_list() -> list[tuple[str]]:
    """
    Fetches list of all series in records, orders by series id

    Returns
    -------
    list[tuple[str]]
        List of tuples of series

    Raises
    ------
    mysql.connector.Error
        If the query fails due to any reason
    """

    cfg.cur.execute("select series_id from series order by series_id")

    return cfg.cur.fetchall() #type: ignore


def fetch_student_list() -> list[tuple[int, str]]:
    """
    Fetches list of all students in records, orders by roll number

    Returns
    -------
    list[tuple[int, str]]
        List of tuples of students
        First element of tuple is roll number while second is name

    Raises
    ------
    mysql.connector.Error
        If the query fails due to any reason
    """

    cfg.cur.execute("select rollno, name from students order by rollno")

    return cfg.cur.fetchall() #type: ignore


def fetch_subject_list() -> list[tuple[str, str]]:
    """
    Fetches list of all subjects, orders by subject id

    Returns
    -------
    list[tuple[str, str]]
        List of tuples of subjects.
        First element of tuple is subject name while second is subject id

        
    Raises
    ------
    mysql.connector.Error
        If the query fails due to any reason
    """
    
    cfg.cur.execute("select name, sid from subjects order by sid")

    return cfg.cur.fetchall() #type: ignore

def fetch_subject_list_by_student(rollno:int) -> list[tuple[str, str]]:
    """
    Fetches list of subjects for a particular student, orders by subject id

    Parameters
    ----------
    rollno : int
        Roll number of student to fetch subjects for

    Returns
    -------
    list[tuple[str, str]]
        List of tuples of subjects.
        First element of tuple is subject name while second is subject id

        
    Raises
    ------
    mysql.connector.Error
        If the query fails due to any reason
    """
    
    query = "select distinct subjects.name, subjects.sid from subjects, results where results.rollno={} and results.sid=subjects.sid order by sid".format(rollno)
    
    cfg.cur.execute(query)

    return cfg.cur.fetchall() #type: ignore

def fetch_subject_list_by_student_series(rollno: int, series: str) -> list[tuple[str, str]]:
    """
    Fetches list of subjects for a particular student and series, orders by subject id

    Parameters
    ----------
    rollno : int
        Roll number of student to fetch subjects for
    series : str
        If only specifc series are to be searched in

    Returns
    -------
    list[tuple[str, str]]
        List of tuples of subjects.
        First element of tuple is subject name while second is subject id

        
    Raises
    ------
    mysql.connector.Error
        If the query fails due to any reason
    """

    if series == "":
        return fetch_subject_list_by_student(rollno)

    query = "select distinct subjects.name, subjects.sid from subjects, results, exams where results.rollno={} and results.sid=subjects.sid and results.eid = exams.eid and exams.series_id='{}' order by sid".format(rollno, series)
    cfg.cur.execute(query)

    return cfg.cur.fetchall() #type: ignore

def fetch_subject_list_by_exam(exam_id:str, include_total:bool=True) -> list[tuple[str, str]]:
    """
    Fetches list of subjects for a particular exam, orders by subject id

    Parameters
    ----------
    exam_id : str
        If only specifc series are to be searched in
    include_total : bool
        If the total subject should be included in the list.
        Will only be added if the subject list contains at least one other subject

    Returns
    -------
    List[Tuple[str, str]]
        List of tuples of subjects.
        First element of tuple is subject name while second is subject id

        
    Raises
    ------
    mysql.connector.Error
        If the query fails due to any reason
    """
    query = "select distinct subjects.name, subjects.sid from subjects, exam_subjects where exam_subjects.eid = '{}' and exam_subjects.sid = subjects.sid order by subjects.sid".format(exam_id)

    cfg.cur.execute(query)

    records = cfg.cur.fetchall()

    if include_total and len(records) > 0:
        records.insert(0, ("Total", "000"))
    
    return records #type: ignore
