import requests
import zk
from datetime import datetime, timedelta
import re         
def get_attendance_data(start_date,end_date,machine_ip,common_key,port):    
    zk_instance = zk.base.ZK(machine_ip, port=int(port), timeout=60, password=str(common_key))
    conn=""
    try:
        conn = zk_instance.connect()
        if conn:
            attendance_data = conn.get_attendance()
            conn.disable_device()
            # Get attendance data
            pattern = r"<Attendance>: (\d+) : (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \((\d+), (\d+)\)"
            attendance_records={}
            for record in attendance_data:
                record_date = record.timestamp.date()
                if(record_date.strftime('%Y-%m-%d')>=start_date and record_date.strftime('%Y-%m-%d')<=end_date):   
                    attendance_string=record
                    match = re.match(pattern,str(attendance_string))
                    if match:
                        user_id = int(match.group(1))
                        timestamp = match.group(2)
                        dict_key=f"{record_date.strftime('%Y-%m-%d')}-{user_id}"
                        if(dict_key not in attendance_records):
                            attendance_records[dict_key]=[str(user_id),timestamp]
                        else:
                            attendance_records[dict_key].append(timestamp)
            conn.enable_device()
            return attendance_records
    except Exception as e:
        print(e)
    finally:
        if conn:
            conn.disconnect()



def send_to_erpnext(erpnext_api_url,erpnext_api_key,attendance_data):
    headers = {
        'Authorization': erpnext_api_key,
        'Content-Type': 'application/json',
    }
    for data in attendance_data:
        user_id=""
        login_time=""
        logout_time=""
        if(len(attendance_data[data])>=1):
            user_id=attendance_data[data][0]
        if(len(attendance_data[data])>=2):
            login_time=attendance_data[data][1]
        if(len(attendance_data[data])>=3):
            list_len=len(attendance_data[data])
            logout_time=attendance_data[data][list_len-1]
        for i in range(2):
            punch_type=""
            if(i==0):
                punch_type="IN"
            elif(i==1):
                punch_type="OUT"
            if(login_time and punch_type=="IN"):
                timespan=login_time
                api_requests(erpnext_api_url,headers,user_id,timespan,punch_type)
            if(logout_time and punch_type=="OUT"):
                timespan=logout_time
                api_requests(erpnext_api_url,headers,user_id,timespan,punch_type)
  
  
                
def api_requests(erpnext_api_url,headers,user_id,timespan,punch_type):
    url = f"{erpnext_api_url}/api/method/hrms.hr.doctype.employee_checkin.employee_checkin.add_log_based_on_employee_field?employee_field_value={str(user_id)}&timestamp={str(timespan)}&log_type={str(punch_type)}"
    response = requests.request("POST", url, headers=headers, data={})
    

