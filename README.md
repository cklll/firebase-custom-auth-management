# What is this project
Firebase provides email-password authentication. However, it does not allow you to send fully customized emails for email verification and password reset. This is a quick example using Flask and Mailgun to let you achieve this.

# How are the problems solved
#### Email verification
1. User creates an account in client side
1. User gets an ID Token and send it to our server (if register successfully)
1. Server generates an JWT token containing Firebase uid
1. Server sends a verification email containing the token (retrieve uid from ID Token then get the email address by adminsdk)
1. User clicks on the verification link
1. Server verify the JWT token and set email verified using adminsdk

#### Password reset
1. User inputs the email address and sends the request to our server
1. Server generates an JWT token containing Firebase uid (if the email exists in Firebase)
1. Server sends a password reset email containing the token to the email address
1. User clicks on the reset link to go to our pgae
1. User inputs and sends the new password to our server along with the token
1. Server verify the JWT token and set the new password using adminsdk

# Tested Platforms
* Python 3.6
* Firebasejs 5.2.0

# Installation

#### Configuration
Copy `config.example.json` to `config.json` and update all the information

#### Python virtual environment 
```
virtualenv . # create a virtual environment in current directory
pip install -r requirements.txt # install dependencies
```

#### Templates
Update the HTML/Email templates in `/templates`

#### Firebase
Download Your Firebase Admin SDK service account json at
https://console.firebase.google.com/project/*{project-name}*/settings/serviceaccounts/adminsdk  

Rename it to `firebase-adminsdk.json` and move to project root directory

#### Mailgun
This projects use Mailgun to send verification and password reset emails. Get an account [here](https://www.mailgun.com/).  

By default, you have a sandbox account and you can *ONLY* send emails to whitelisted email addresses which you can defined in the dashboard.  

If you wish to use your own domain, check the [documentation](https://documentation.mailgun.com/en/latest/user_manual.html#verifying-your-domain) for details

# Screenshots
*TODO*