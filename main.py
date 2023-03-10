class SiwoPasswordSecurityChecker():

    def __init__(self):
        self.password = ""
        pass

    def request_api_data(self):
        import requests
        url = 'https://api.pwnedpasswords.com/range/' + self.password[:5]
        res = requests.get(url)
        if res.status_code != 200:
            raise RuntimeError(f"Error fetching: {res.status_code}, check the API again")
        return res

    def request_api_read(self, datas):
        print(datas.text)

    def set_password(self, password):
        self.password = password

    def sha1_password(self, password):
        import hashlib
        return (hashlib.sha1(password.encode("utf-8")).hexdigest()).upper()

    def password_check(self, password):
        self.set_password(self.sha1_password(password))
        return self.password_leaks_count(self.request_api_data().text, self.password[5:])

    def password_leaks_count(self, hashes, check):
        hashes = (line.split(":") for line in hashes.splitlines())
        for h, count in hashes:
            if h == check:
                return count
        return 0

    def enter_passwords(self):
        passwords = []
        input_label = "Enter passwords, one by line, then double-enter, or 'q' to quit: "
        while True:
            saisie = input(input_label)
            if saisie == 'q':
                return None
            elif saisie == '':
                break
            else:
                input_label = ''
                passwords.append(saisie)
        return self.store_passwords(passwords)

    def store_passwords(self, passwords):
        with open(self.config_parser().get("password", "file"), "w") as file:
            for password in passwords:
                file.write(password)
                file.write('\n')
        return True

    def get_passwords(self):
        with open(self.config_parser().get("password", "file"), "r") as file:
            return file.readlines()

    def send_mail(self, message):
        import smtplib

        sender_email = self.config_parser().get("smtp", "email")
        receiver_email = self.config_parser().get("smtp", "email")
        password = self.config_parser().get("smtp", "password")

        server = smtplib.SMTP(self.config_parser().get("smtp", "smtp_host"),
                              self.config_parser().get("smtp", "smtp_port"))
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
        server.quit()

    def check_passwords(self):
        import os.path
        while True:
            if not os.path.exists(self.config_parser().get("password", "file")):
                self.enter_passwords()
            else:
                for password in self.get_passwords():
                    checking = self.password_check(password)
                    if int(checking) > 0:
                        #print(f"Password '{password}' have been pwned {checking} times. You should change this password !")
                        self.send_mail(
                            f"Password '{password}' have been pwned {checking} times. You should change this password !")
                break

    def config_parser(self):
        from configparser import ConfigParser
        config = ConfigParser()
        config.read('config.ini')
        return config


if __name__ == '__main__':
    main = SiwoPasswordSecurityChecker()
    main.check_passwords()
