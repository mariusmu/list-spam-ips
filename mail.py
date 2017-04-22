import imaplib
import email
import operator
import re

host = "" # Type the imap host
username = "" # Type imap user name
password = "" # Type imap password
folder = "Spam" # Type which folder to select messages from
verbose = False # Should the file output be verbose
filename = 'output.txt' # Type the output file name

class FileWriter:
    """
    Simple file writer class to write the spam output
    to file
    """
    def persist(self, lst):
        """
        Write the output IPs to file
        :param lst: The list containing the Spam messages
        :return: Method will return empty
        """
        lst = sorted(lst.items(), key=operator.itemgetter(0))

        f = open(filename, 'w')
        try:
            for key, item in lst:
                f.write("{}".format(key))
                if verbose:
                    f.write(" [{}] - Sender: {} ".format(len(item.lst), item.lst[0].sender))
                f.write("\n")
            f.close()
        except IOError as e:
            print("FileWriter.persist(): {}".format(e))


class SpamMail:
    """
    A class that represent the spam mail
    """
    def __init__(self, ip, sender, subject, date):
        self.ip = ip
        self.sender = sender
        self.subject = subject
        self.date = date


class ContainerItem:
    """
    A oontainer item to be inserted into the container
    map
    """
    def __init__(self, SpamMail):
        self.lst = []
        self.lst.append(SpamMail)

    def add(self, SpamMail):
        """
        Add a spam mail to the container item list
        :param SpamMail: The spam mail to insert
        :return: Method returns empty
        """
        self.lst.append(SpamMail)
        return self

    def count(self):
        """
        Return the number of spam mails from this sender
        :return: The number of spam mails from this sender
        """
        return len(self.lst)

class Container:
    """
    A simple container (Map)
    """
    def __init__(self):
        self.lst = {}

    def persist(self):
        """
        Persist the map content into a file
        :return: method returnes empty
        """
        FileWriter().persist(self.lst)

    def add(self, ip, SpamMail):
        """
        Add a spam entry into a container item
        based on ip
        :param ip: the ip of the sender
        :param SpamMail: the spam mail to insert
        :return: method returnes empty
        """
        try:
            if not self.lst.__contains__(ip):

                item = ContainerItem(SpamMail)
                self.lst.update({ip:item})
            else:
                curr = self.lst[ip]
                self.lst.update({ip:curr.add(SpamMail)})

        except:
            print("Caontiner.add()")

    def print_lst(self):
        """
        Print the content of the container
        :return: method returns empty
        """
        sort = sorted(self.lst.items(), key=operator.itemgetter(0))
        print(sort)
        for elem, var in sort:
            print(elem, var.count(), self.lst.get(elem).lst[0].sender)


class ImapMail:
    """
    Imap mail service class
    """
    mail = imaplib.IMAP4_SSL(host)

    def __init__(self):
        self.container = Container()

    def login(self):
        """
        Log in to the server
        :return: method returns empty
        """
        try:
            self.mail.login(username, password)
        except imaplib.IMAP4.error as e:
            print(e)

    def select(self):
        """
        Select all mails from a IMAP directory
        :return: method returns empty
        """
        try:
            self.mail.select(folder)
            result, data = self.mail.uid('search', None, "ALL")
            ids = data[0]
            id_list = ids.split()
            for attr in id_list:
                result, currdata = self.mail.uid('fetch', attr, '(RFC822)')
                self.parse(currdata[0])
            self.container.print_lst()
            self.container.persist()

        except imaplib.IMAP4.error as e:
            print("ImapMail.select(): {}".format(e))


    def parse(self, elem):
        """
        Parse the raw imap mail into a SpamMessage object
        :param elem: the raw imap object
        :return: method returns empty
        """
        try:
            res = email.message_from_string(elem[1].decode("utf-8", errors='ignore'))
            ip = re.match(r"[^[]*\[([^]]*)\]", res['Received']).groups()[0]
            sender = re.findall(r'<(.+?)>', res['Received'])[0]
            date = res['Delivery-date']
            subject = res['Subject']
            self.container.add(ip, SpamMail(ip, sender, subject, date))

        except (re.error, imaplib.IMAP4.error) as e:
            print("ImapMail.parse(): {}".format(e))


def init():

    y = ImapMail()
    print("Fetchig messages from SPAM folder")
    y.login()
    y.select()

if (__name__ == "__main__"):
   init()
