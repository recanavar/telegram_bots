import requests
import time
import os

github_url = "https://github.com/rapid7/metasploit-framework/blob/master/"

def get_additional_info():
    additional_info = os.popen('cat git_pull_upstream.txt | grep "create mode"').readlines()
    return additional_info

def get_changelog_info():
    changelog_info = os.popen('cat git_pull_upstream.txt | grep "insertions(+)"').read()
    return changelog_info.strip().replace("+","%2B")

def get_files_with_msf_path():
    files = os.popen('cat git_pull_upstream.txt | grep -e "|" | cut -d"|" -f1 |cut -d " " -f2').readlines()
    return files

def get_links(files):
    links = []
    for i in files:
        if i[0:3] == "...":
            link = get_msf_file_path(i[3:].rstrip())
            links.append(github_url+link)
        else:
            links.append(github_url+i)
    return links

def get_changes():
    temp_changes = os.popen('cat git_pull_upstream.txt | grep -e "|" | cut -d"|" -f2').readlines()
    changes = []
    for i in temp_changes:
        changes.append(i.strip().replace("+","%2B"))
    return changes

# Getting file absolute path beginning with "..." from cloned Metasploit files.
def get_msf_file_path(file_path):
    os_path = '<YOUR_METASPLOIT_FRAMEWORK_PATH>' # without "<" and ">", for example: /home/user/tools/metasploit-framework
    msf_file_paths = []
    msf_file_path = ""

    for r,d,f in os.walk(os_path):
        for i in f:
            msf_file_paths.append(os.path.join(r,i))

    for path in msf_file_paths:
        if file_path in path:
            msf_file_path = path
    return msf_file_path.replace(os_path,"")

def get_date():
    date = os.popen('date').read().strip()
    return date

# Parsing output and creating message to send telegram channel
def message(files, changes, links, additional_info, changelog_info):
    date = os.popen('date').read().strip()
    temp_changes = ["*Changes* \n```\nFile | Changes ", "----------------"]
    for i in range(len(files)):
        temp_changes.append(str(i+1) + ". " + files[i].rstrip() + " | " + changes[i].rstrip()) # "| " + + " |"
    channel_changes = "\n".join(line.strip() for line in temp_changes) + "\n```"

    temp_links = ["*Links*\n"]
    for i in range(len(files)):
        temp_links.append(str(i+1) + ".  " + "["+files[i].rstrip() + "]" + "(" + links[i].rstrip() + ")")
    channel_links = "\n".join(line.strip() for line in temp_links)

    temp_additional_info = ["*Additional Info*\n```"]
    for i in range(len(additional_info)):
        temp_additional_info.append(">" + additional_info[i].rstrip())
    additional_infos = "\n".join(line.strip() for line in temp_additional_info) + "\n```"

    message = "*Date: " + date + " *\n\n" + channel_changes + "\n" + channel_links + "\n\n" + additional_infos + "\n" + "* " + changelog_info + " *"

    return message

def telegram_bot_sendtext(text):
    bot_token = '<YOUR_BOT_TOKEN>' # your bot token without "<" and ">"
    bot_channelID = '<YOUR_CHANNEL_ID>' #  your channel id without "<" and ">"
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?disable_web_page_preview=True' + '&chat_id=' + bot_channelID + '&parse_mode=Markdown&text=' + text

def main():
    control = os.popen('cat git_pull_upstream.txt').read().strip()
    if control == "Already up to date.":
        f = open('logs.txt','a+')
        f.write(get_date() + ": " + control + "\n")
        f.close()
    else:
        changes = get_changes()
        files = get_files_with_msf_path()
        links = get_links(files)
        additional_info = get_additional_info()
        changelog_info = get_changelog_info()
        telegram_message = message(files, changes, links, additional_info, changelog_info)
        telegram_bot_sendtext(telegram_message)
        f = open('logs.txt', 'a+')
        f.write(get_date() + ": " + changelog_info + "\n")
        f.close()

if __name__ == "__main__":
    main()