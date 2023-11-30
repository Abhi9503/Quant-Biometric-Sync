import requests
import zk
from datetime import datetime, timedelta
import re   


def get_attendance_data(start_date,end_date,machine_ip,common_key):    
    conn=""
    zk_instance = zk.base.ZK(machine_ip, port=4370, timeout=60, password=common_key)
    try:
        conn = zk_instance.connect()
        if conn:
            attendance_data = conn.get_attendance()
            conn.disable_device()
            # Get attendance data
            pattern = r"<Attendance>: (\d+) : (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \((\d+), (\d+)\)"
            attendance_records=[]
            for record in attendance_data:
                record_date = record.timestamp.date()
                if(record_date.strftime('%Y-%m-%d')>=start_date and record_date.strftime('%Y-%m-%d')<=end_date):
                    # print(record)
                    attendance_string=record
                    match = re.match(pattern,str(attendance_string))
                    if match:
                        user_id = int(match.group(1))
                        timestamp = match.group(2)
                        in_value = int(match.group(3))
                        out_value = int(match.group(4))
                        # if(user_id==1019 or user_id==1021):
                        attendance_records.append({"id":user_id,"timestamp":timestamp,"in_value":in_value,"out_value":out_value})
            conn.enable_device()
            return attendance_records
    finally:
        if conn:
            conn.disconnect()


def send_to_erpnext(erpnext_api_url,erpnext_api_key,attendance_data):
    headers = {
        'Authorization': erpnext_api_key,
        'Content-Type': 'application/json',
    }
    
    punch_type=""
    for data in attendance_data:
        if(int(data["out_value"])>0):
            punch_type="OUT"
        else:
            punch_type="IN"
            
        payload = {}
        url = f"{erpnext_api_url}/api/method/hrms.hr.doctype.employee_checkin.employee_checkin.add_log_based_on_employee_field?employee_field_value={str(data['id'])}&timestamp={data['timestamp']}&log_type={str(punch_type)}"
        response = requests.request("POST", url, headers=headers, data=payload)
       



machine_ip="192.168.1.33"
start_date ="2023-11-28"
end_date ="2023-11-28"
common_key ="41410"

# erpnext_api_url=sc.erpnext_api_url
# erpnext_api_key=sc.erpnext_api_key

if __name__=="__main__":
    attendance_data=get_attendance_data(start_date,end_date,machine_ip,common_key)
    for i in attendance_data:
        print(i)
    # send_to_erpnext(erpnext_api_url,erpnext_api_key,attendance_data)