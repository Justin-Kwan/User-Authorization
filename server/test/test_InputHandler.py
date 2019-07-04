import pytest
import sys
sys.path.append('/Users/justinkwan/Documents/WebApps/UserAuth/server/src/BusinessLayer/handlers')
sys.path.append('/Users/justinkwan/Documents/WebApps/UserAuth/server/src/DataBaseLayer')
sys.path.append('/Users/justinkwan/Documents/WebApps/UserAuth/server/src/BusinessLayer/models')
from InputHandler     import InputHandler
from DatabaseAccessor import DatabaseAccessor
from User             import User

inputHandler = InputHandler()
DBA = DatabaseAccessor()

def getUser(username, password):
    user = User(username, password)
    user.encryptAndUpdatePassword(password)
    user.generateAndUpdateUserId()
    return user

def test_checkInputNull():
    assert inputHandler.checkInputNull(None, None) == 'EMPTY_FIELDS'
    assert inputHandler.checkInputNull(None, 'password123') == 'EMPTY_USERNAME'
    assert inputHandler.checkInputNull('username123', None) == 'EMPTY_PASSWORD'
    assert inputHandler.checkInputNull('username123', 'password123') == 'ALL_FIELDS_FILLED'

def test_checkTextEmpty():
    assert inputHandler.checkTextEmpty('Not Empty') == False
    assert inputHandler.checkTextEmpty('') == True
    assert inputHandler.checkTextEmpty('0987*') == False

# testing username and password length constraints for input validation
def test_checkInputLength():
    # middle case
    assert inputHandler.checkInputLength('USERNAME', 'testusername') == True
    # edge case
    assert inputHandler.checkInputLength('USERNAME', 'usrnmm') == True
    assert inputHandler.checkInputLength('USERNAME', 'testusernametestusernametestusernam') == True
    assert inputHandler.checkInputLength('USERNAME', 'testusernametestusernametestusername') == False
    assert inputHandler.checkInputLength('USERNAME', 'usrnm') == False
    assert inputHandler.checkInputLength('USERNAME', '') == False
    assert inputHandler.checkInputLength('USERNAME', 'testusernametestusernametestusernametestusernametestusernametestusername') == False

    assert inputHandler.checkInputLength('PASSWORD', 'usrnmmff') == True
    assert inputHandler.checkInputLength('PASSWORD', 'testusernametestusernametestusernam') == True
    assert inputHandler.checkInputLength('PASSWORD', 'testusernametestusernametestusernametestusernametestusernametestu;') == False
    assert inputHandler.checkInputLength('PASSWORD', 'usrnmdd') == False
    assert inputHandler.checkInputLength('PASSWORD', '') == False
    assert inputHandler.checkInputLength('PASSWORD', 'testusernametestusernametestusernametestusernametestusernametestu') == True
    assert inputHandler.checkInputLength('PASSWORD', 'testusernametestusernametestusernametestusernametestusernametestusername') == False

def test_handleEmptyFields():
    user = getUser('', '')
    assert inputHandler.handleEmptyFields(user) == 'EMPTY_FIELDS'
    del user

    user = getUser('', 'password')
    assert inputHandler.handleEmptyFields(user) == 'EMPTY_USERNAME'
    del user

    user = getUser('username', '')
    assert inputHandler.handleEmptyFields(user) == 'EMPTY_PASSWORD'
    del user

    user = getUser('username', 'password')
    assert inputHandler.handleEmptyFields(user) == 'ALL_FIELDS_FILLED'
    del user

def test_handleInputLengthChecks():
    user = getUser('NewUser123', 'testusername')
    assert inputHandler.handleInputLengthChecks(user) == 'GOOD_USERNAME_&_PASSWORD_LENGTH'
    del user

    user = getUser('usrnmm', 'testusernametestusernametestusernam')
    assert inputHandler.handleInputLengthChecks(user) == 'GOOD_USERNAME_&_PASSWORD_LENGTH'
    del user

    user = getUser('testusernametestusernametestusername', 'testusernametestusernametestusernametestusernametestusernametestu;')
    assert inputHandler.handleInputLengthChecks(user) == 'INVALID_USERNAME_LENGTH'
    del user

    user = getUser('', 'usrnmdd')
    assert inputHandler.handleInputLengthChecks(user) == 'INVALID_USERNAME_LENGTH'
    del user

    user = getUser('User', '')
    assert inputHandler.handleInputLengthChecks(user) == 'INVALID_USERNAME_LENGTH'
    del user

    user = getUser(',', 'testusernametestusernametestusernametestusernametestusernametestusername')
    assert inputHandler.handleInputLengthChecks(user) == 'INVALID_USERNAME_LENGTH'
    del user

    user = getUser('usrnmm', 'testusernametestusernametestusernametestusernametestusernametestu')
    assert inputHandler.handleInputLengthChecks(user) == 'GOOD_USERNAME_&_PASSWORD_LENGTH'
    del user

    user = getUser('usrnmm', 'testusernametestusernametestusernametestusernametestusernametestus')
    assert inputHandler.handleInputLengthChecks(user) == 'INVALID_PASSWORD_LENGTH'
    del user

    user = getUser('usrnmm', 'passwor')
    assert inputHandler.handleInputLengthChecks(user) == 'INVALID_PASSWORD_LENGTH'
    del user

def test_checkForInvalidUsernameChars():
    user = getUser('string2', 'password123')
    assert inputHandler.checkForInvalidUsernameChars(user) == True
    del user

    user = getUser('fake$username)', 'password123')
    assert inputHandler.checkForInvalidUsernameChars(user) == False
    del user

    user = getUser(')(*&^)', 'password123')
    assert inputHandler.checkForInvalidUsernameChars(user) == False
    del user

    user = getUser(')(*&^)textTest*&^%moretestis*fun;:', 'password123')
    assert inputHandler.checkForInvalidUsernameChars(user) == False
    del user

def test_verifyPassword():
    user1 = getUser('username1', 'password1')
    DBA.insertUserInfo(user1)
    user2 = getUser('username1', 'password1')
    selectedHashedPassword = DBA.selectHashedPassword(user2).encode('utf-8')
    isPasswordCorrect = inputHandler.verifyPassword(user2, selectedHashedPassword)
    assert isPasswordCorrect == True

    del user1
    del user2
    DBA.clearDatabase()

    user1 = getUser('username2', 'password2')
    DBA.insertUserInfo(user1)
    user2 = getUser('username2', 'password1')
    selectedHashedPassword = DBA.selectHashedPassword(user2).encode('utf-8')
    isPasswordCorrect = inputHandler.verifyPassword(user2, selectedHashedPassword)
    assert isPasswordCorrect == False

    del user1
    del user2
    DBA.clearDatabase()

    user1 = getUser('username3', '^&*()()')
    DBA.insertUserInfo(user1)
    user2 = getUser('username3', '^&*()()')
    selectedHashedPassword = DBA.selectHashedPassword(user2).encode('utf-8')
    isPasswordCorrect = inputHandler.verifyPassword(user2, selectedHashedPassword)
    assert isPasswordCorrect == True

    del user1
    del user2
    DBA.clearDatabase()
