#!/usr/bin/env python3
import json
import requests

####################################
# written by:   Mike Rieben
# e-mail:       mrieben@extremenetworks.com
# date:         6th October 2022
# version:      2.0
####################################
# ACTION ITEMS / PREREQUISITES
# Modify values in Gloabl Variables section below
# 1) XIQ_username
# 2) XIQ_password
# This script can be augmented to not use embedded credentials.  See Time Smith's Python scripts for exampls.
####################################


# Gloabl Variables are stored upon running the script
XIQ_username = "<email>"  # enter your XIQ username within "" (Operator or higher)
XIQ_password = "<pass>"  # enter your XIQ password within "" (Operator or higher)
XIQ_url = "https://api.extremecloudiq.com"  # XIQ's API portal
headers = {"Accept": "application/json", "Content-Type": "application/json"}  # I have no idea why this is required but it is when sending the API
payload = json.dumps({"username": XIQ_username, "password": XIQ_password})  # prepare the payload in json format for XIQ credentials
response = requests.post(XIQ_url, headers=headers, data=payload)  # send the API payload to read the response and gather the token
vlanProtectList = [40000,40001]  # VLAN Profile IDs that will not be deleted if that option was chosen.  40000 & 40001 are default objects.
userProfileProtectList = [36000,36001]  # User Profile IDs that will not be deleted.  36000 & 36001 are default objects.


# Function to get XIQ access token
def getAccessToken(XIQ_username, XIQ_password):
	url = XIQ_url + "/login"  # This is the API specific path https://api.extremecloudiq.com/login.  Can get this off the Swagger UI or Postman.
	payload = json.dumps({"username": XIQ_username, "password": XIQ_password})  # Prepare the payload with the XIQ credentials in json format
	response = requests.post(url, headers=headers, data=payload)  # Send the API call
	if response is None:
		log_msg = "ERROR: Not able to login into ExtremeCloudIQ - no response!"
		#logging.error(log_msg)  # omitted logging for now
		raise TypeError(log_msg)
	if response.status_code != 200:
		log_msg = f"Error getting access token - HTTP Status Code: {str(response.status_code)}"
		#logging.error(f"{log_msg}")  # omitted logging for now
		#logging.warning(f"\t\t{response}")  # omitted logging for now
		raise TypeError(log_msg)
	data = response.json()
	if "access_token" in data:
		#print("Logged in and Got access token: " + data["access_token"])  # omitted for a cleaner user experience
		headers["Authorization"] = "Bearer " + data["access_token"]
		return 0
	else:
		log_msg = "Unknown Error: Unable to gain access token. Aborting script..."
		#logging.warning(log_msg)  # omitted logging for now
		raise TypeError(log_msg)
		

# Function to create VLANs & User Profiles
def createVLANs(vlanCreate,endVlan,createUserProfile):
	url2 = XIQ_url + "/vlan-profiles"
	url3 = XIQ_url + "/user-profiles" #User Profile feautre
	while vlanCreate <= endVlan:
		payload = json.dumps({"name": str(vlanCreate), "default_vlan_id": vlanCreate, "enable_classification": "false"})  # Prepare the payload with the VLAN object info
		print("Creating VLAN: " + str(vlanCreate))  # Print to screen when it creates a VLAN and the ID#
		response = requests.post(url2, headers=headers, data=payload, verify=True)  # Send the API call
		#print(response.text) #debugging - print to screen the API response
		data = (response.json()) #User Profile feautre
		vlan_id = data['id'] #User Profile feautre
		#print("VLAN ID:" + str(vlan_id)) #print VLAN ID to screen
		if createUserProfile == "Yes": #User Profile feautre
			payload2 = json.dumps({"name": str(vlanCreate), "vlan_profile_id": vlan_id}) #User Profile feautre
			response = requests.post(url3, headers=headers, data=payload2, verify=True) #User Profile feautre
			print("Creating User Profile: " + str(vlanCreate)) #User Profile feautre
			#print("Creating User Profile: " + str(vlanCreate) + ", VLAN ID: " + str(vlan_id)) #User Profile feautre - more info printed to screen
		else:
			print("Skipping User Profile creation")
		vlanCreate = vlanCreate + 1  # increment +1 for the while loop


# Function to gather a list of VLAN Profiles
def retrieveVLANProfiles():
	# if you have multiple pages of VLAN objects this will gather all pages
    page = 1
    pageCount = 1
    firstCall = True
    vlanProfiles = []
    while page <= pageCount:
        url = XIQ_url + "/vlan-profiles?page=" + str(page) + "&limit=100" 
        response = requests.get(url, headers=headers, verify=True)
        if response is None:
            log_msg = f"ERROR: Not able to collect vlan profiles from ExtremeCloudIQ - no response!"
            raise TypeError(log_msg)
        if response.status_code != 200:
            log_msg = f"Error collecting vlan profiles - HTTP Status Code: {str(response.status_code)}"
            raise TypeError(log_msg)
        data = response.json()
        vlanProfiles = vlanProfiles + data['data']
        if firstCall ==True:
            pageCount = data['total_pages']
        print(f"Completed page {page} of {data['total_pages']} collecting VLAN Profiles")
        page = data['page'] + 1
    return vlanProfiles


# Function to delete VLAN objects
def deleteVLANs(vlan_id, name):
    url = XIQ_url + "/vlan-profiles/" + str(vlan_id)
    response = requests.delete(url, headers=headers, verify=True)
    if response is None:
        log_msg = f"ERROR: Not able to delete vlan {name} ExtremeCloudIQ - no response!"
        raise TypeError(log_msg)
    if response.status_code != 200:
        log_msg = f"Error deleting vlan {name} - HTTP Status Code: {str(response.status_code)}"
        raise TypeError(log_msg)
    print(f"Successfully deleted VLAN: {name}")


# Function to gather a list of User Profiles
def retrieveUserProfiles():
	# if you have multiple pages of User Profile objects this will gather all pages
    # login = getAccessToken(XIQ_username, XIQ_password)
    page = 1
    pageCount = 1
    firstCall = True
    userProfiles = []
    while page <= pageCount:
        url = XIQ_url + "/user-profiles?page=" + str(page) + "&limit=100" 
        response = requests.get(url, headers=headers, verify=True)
        #print(response)
        if response is None:
            log_msg = f"ERROR: Not able to collect user profiles from ExtremeCloudIQ - no response!"
            raise TypeError(log_msg)
        if response.status_code != 200:
            log_msg = f"Error collecting user profiles - HTTP Status Code: {str(response.status_code)}"
            raise TypeError(log_msg)
        data = response.json()
        userProfiles = userProfiles + data['data']
        if firstCall ==True:
            pageCount = data['total_pages']
        print(f"Completed page {page} of {data['total_pages']} collecting User Profiles")
        page = data['page'] + 1
    return userProfiles
    # print(userProfiles)


#Function to delete User Profile objects
def deleteUserProfiles(user_prof_id, name):
    url = XIQ_url + "/user-profiles/" + str(user_prof_id)
    response = requests.delete(url, headers=headers, verify=True)
    if response is None:
        log_msg = f"ERROR: Not able to delete User Profile {name} ExtremeCloudIQ - no response!"
        raise TypeError(log_msg)
    if response.status_code != 200:
        log_msg = f"Error deleting User Profile {name} - HTTP Status Code: {str(response.status_code)}"
        raise TypeError(log_msg)
    print(f"Successfully deleted User Profile: {name}")


# This fucntion will run first
def main():
	try:
		login = getAccessToken(XIQ_username, XIQ_password)
	except TypeError as e:
		print(e)
		raise SystemExit
	except:
		log_msg = "Unknown Error: Failed to generate token"
		print(log_msg)
		raise SystemExit

	print("\nThis script has two options:\n\n1) Create VLANs between a range of numbers.\n - VLAN object name will match the VLAN ID.\n - A corresponding User Profile may be created.\n\n2) Delete all VLANs & User Profiles to start over.\n")
	try:
		initOptions = int(input("Do you want to (1)Create or (2)Delete VLANs? [1|2]: "))
	except ValueError as e:
		print("You must enter 1 or 2: Aborting script...")
		raise SystemExit
	except:
		print("Unknown Error: Aborting script...")
		raise SystemExit
	# If the user enters a 1 to create VLANs
	if initOptions == 1:
		try:
			vlanCreate = int(input("Enter first VLAN ID (1~4094) to create: "))
		except ValueError as e:
			print("You must enter a number from 1 to 4094: Aborting script...")
			raise SystemExit
		except:
			print("Unknown Error: Aborting script...")
			raise SystemExit
		try:
			endVlan = int(input("Enter last VLAN ID (1~4094) to create: "))
		except ValueError as e:
			print("You must enter a number from 1 to 4094: Aborting script...")
			raise SystemExit
		except:
			print("Unknown Error: Aborting script...")
			raise SystemExit
		# Check if the user entered a valid VLAN within range.  If not, abort.
		if 0 <= vlanCreate <= 4094 and 0 <= endVlan <= 4094:
			createUserProfile = input("Create a corresponding User Profile? [Yes|No] ").upper()
			if createUserProfile == "Y" or createUserProfile == "YE" or createUserProfile == "YES":
				createUserProfile = "Yes"
			elif (createUserProfile == "N") or (createUserProfile == "NO"):
				createUserProfile = "No"
			else:
				print("Must provide a valid answer Yes or No.")
				raise SystemExit
			createVLANs(vlanCreate,endVlan,createUserProfile)
		else:
			print(f"Invalid VLAN ID entry: {vlanCreate} or {endVlan}. Aborting script...")
			raise SystemExit
	# If the user enters a 2 to delete VLANs
	elif initOptions == 2:
		print ("\n*** CAUTION NUCLEAR OPTION CHOSEN *** User Profiles MUST be deleted since they're a dependency. ***")
		deleteVLANsQ = input("\nAre you sure you want to DELETE all VLANs & USER PROFILES? [Yes|No]: ").upper()
		# If the user enters YES to confirm delete VLANs
		if deleteVLANsQ == "Y" or deleteVLANsQ == "YE" or deleteVLANsQ == "YES":
			# User Profiles must be deleted first before VLANs
			user_profiles = retrieveUserProfiles()
			for user_prof in user_profiles:
				if user_prof['id'] in userProfileProtectList:
					continue
				else:
					try:
						deleteUserProfiles(user_prof["id"],user_prof['name'])
					except TypeError as e:
						print(e)
					except:
						print(f"Unknown Error: Couldn't delete user profile {user_prof['name']}. Check Used By column in XIQ.")
			# VLANs will be deleted after User Profiles
			vlan_profiles = retrieveVLANProfiles()
			for vlan in vlan_profiles:
				if vlan['id'] in vlanProtectList:
					continue
				else:
					try:
						deleteVLANs(vlan["id"],vlan['name'])
					except TypeError as e:
						print(e)
					except:
						print(f"Unknown Error: Couldn't delete vlan {vlan['name']}. Check Used By column in XIQ.")
			
		# If the user enters anything but YES to skip deleting VLANs. Script ends here.
		else:
			print("VLANs will not be deleted.")
			raise SystemExit
	# If the user doesn't provide a 1 or 2 for initOptions question. Script ends here.
	else:
		print("Must provide a valid answer, type 1 or 2. Script aborted...")
		raise SystemExit


# Python will see this and run whatever function is provided: main(), should be the last item in this file
if __name__ == '__main__':
	main() # call this function, only one should be here
