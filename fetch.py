from ftplib import FTP

from io import BytesIO
import re, datetime, json

# http://www.posti.fi/liitteet-yrityksille/ehdot/postinumeropalvelut-palvelukuvaus-ja-kayttoehdot.pdf

itella_server = "ftp2.itella.com"
folder = "/unzip/"


ftp = FTP(itella_server)
ftp.login("postcode", "postcode")
ftp.cwd(folder)
files = []

# Fetching filelist and finding the latest records
print("Fetching records...")
ftp.retrlines('NLST', lambda fn: files.append(fn))
postcodes_filename = str(next(filter(lambda file: 'PCF' in file, files)))


# Retrieving the file
postcode_raw_data = BytesIO()
ftp.retrbinary('RETR ' + postcodes_filename, postcode_raw_data.write)
ftp.quit()
postcode_raw_data.seek(0)
postcode_records = postcode_raw_data.read().decode('latin-1').split('\n')
print("Fetched!")
# Different structures
postcode_list = []
postcode_to_record = {}
postcode_to_record_light = {}

print("Parsing records...")
for postcode_record in postcode_records:
    m = re.match(r'^PONOT(?P<date>.{8})(?P<postcode>.{5})(?P<postcode_fi_name>.{30})(?P<postcode_sv_name>.{30})(?P<postcode_abbr_fi>.{12})(?P<postcode_abbr_sv>.{12})(?P<valid_from>.{8})(?P<type_code>.{1})(?P<ad_area_code>.{5})(?P<ad_area_fi>.{30})(?P<ad_area_sv>.{30})(?P<municipal_code>.{3})(?P<municipal_name_fi>.{20})(?P<municipal_name_sv>.{20})(?P<municipal_language_ratio_code>.{1})', postcode_record)
    if m:
        r = { k:v.strip() for k, v in m.groupdict().items()}
        postcode_list.append(r)
        postcode_to_record[r['postcode']] = r
        # For lite version only one name so the filesize is small as possible
        # If municipality is swedish speaking then use swedish name for the code otherwise stick in finnish version
        if r['municipal_language_ratio_code'] in ['1', '2']:
            name = r['postcode_fi_name']
        else:
            name = r['postcode_sv_name']
        postcode_to_record_light[r['postcode']] = name
print("Parsed!")
print("Saving...")

# Save the output
json.dump(postcode_list, open('postcodes.json', 'w'))
json.dump(postcode_to_record, open('postcode_map.json', 'w'))
json.dump(postcode_to_record_light, open('postcode_map_light.json', 'w'))
open('LAST_UPDATED', 'w').write(datetime.datetime.now().isoformat())
print("DONE! BYE!")
