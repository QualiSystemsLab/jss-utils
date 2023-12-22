

# Using requests
report_file = open(c"/temp/report.html', 'rb')
r = requests.put(url=f'{server_url}/api/testexecution/{execution_id}/report/upload',
                 headers={'Authorization': auth_code},
				 files={"reportFile": ("report", report_file, "text_html")},
				 verify=False
				 )
				 

				 
				 
# Using httpx
report_file = open(c"/temp/report.html', 'rb')
report_file.seek(0, os.SEEK.SET)
async with httpx.AsyncClient() as client:
  await client.put(f'{server_url}/api/textexecution/{execution_id}/report/upload',
                   files={"reportFile": report_file})
                   