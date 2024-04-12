import json
import csv
import sys

def read_json(input_file):
    """Reads a JSON file and returns the data."""
    with open(input_file, 'r') as file:
        data = json.load(file)
    return data

def read_students_csv(filename):
    """Reads a CSV file and returns a dictionary mapping UWIDs to student data."""
    uwid_to_student = {}
    with open(filename, mode='r', newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            uwid = row['UWID']
            student_data = {'Name': row['Name'], 'Points': 0}
            uwid_to_student[uwid] = student_data
    return uwid_to_student

def filter_students(cur_thread_data, students_names_uwid):
    """Filters student data based on thread comments and updates points."""
    queue = [comment for comment in cur_thread_data['comments']]
    
    while queue:
        comment = queue.pop()
        email = comment['user']['email']
        uwid = email[:email.index('@')]
        
        if uwid in students_names_uwid and students_names_uwid[uwid]['Points'] == 0:
            students_names_uwid[uwid]['Points'] = 1

        if 'comments' in comment and comment['comments']:
            queue.extend(comment['comments'])

def write_csv(students, output_file):
    """Writes student data to a CSV file."""
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'UWID', 'Points'])
        for uwid, student in students.items():
            writer.writerow([student['Name'], uwid, student['Points']])

def main(threads_filename, students_filename, thread_id, csv_filename):
    """Processes thread data to determine student participation."""
    threads_data = read_json(threads_filename)
    cur_thread_data = next((thread for thread in threads_data if thread_id in thread["url"]), None)
    
    if cur_thread_data is None:
        print(f"Thread doesn't contain data for {thread_id}")
        return

    students_names_uwid = read_students_csv(students_filename)
    filter_students(cur_thread_data, students_names_uwid)
    students_names_uwid = dict(sorted(students_names_uwid.items(), key=lambda x: x[1]['Name']))
    
    write_csv(students_names_uwid, csv_filename)
    print(f"Data has been successfully written to {csv_filename}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print('Error: Needs at least 3 arguments - JSON file path, CSV file path, and thread ID.')
    else:
        try:
            threads_filename = sys.argv[1]
            students_filename = sys.argv[2]
            thread_id = sys.argv[3]
            csv_filename = 'student_participation.csv'
            main(threads_filename, students_filename, thread_id, csv_filename)
        except Exception as e:
            print(f'Error when processing data: {e}')
