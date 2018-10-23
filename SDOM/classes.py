import datetime

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import QRect, QPropertyAnimation

from main import switch_screen, logClose
from main import sqlaccess as sql

UIstem = "/home/dietpi/Code/Python/SUPERDOPE/SDOM/UI/"

current_date = datetime.datetime.now().strftime("%m-%d-%Y")
print current_date

workspace = []

class material:
    def __init__(self,ID,Name,Form,Stage,Source,Location,Active,Notes=None,Forked_From=None):
        self.ID = ID
        self.Name = Name
        self.Form = Form
        self.Stage = Stage
        self.Source = Source
        self.Location = Location
        self.Active = Active
        self.Notes = Notes
        self.Forked_From = Forked_From
        self.Record = [self.ID,self.Name,self.Form,
                       self.Stage,self.Source,self.Location,
                       self.Notes,self.Forked_From,self.Active]
        self.split_list = None
              
    # Examples:
    # No Weight: material.split('noweight,#:5') splits into 5 unweighed containers
    # Weight: material.split('even,amt:4') splits into an arbitrary number of 4 pound containers
    # Weight: material.split() prompts the user for new containers until weight is gone                   
    def split(self,arg=None):
        # first, temporarily write the current material for copying purposes
        self.write()
        # then set temporary local variables
        noWeight = False
        numberContainers = 0
        evenSplit = False
        amountPerContainer = 0
        weight = 0
        set_container_no_amount = False
        if arg != None:
            if '#:' in arg:
                argsplit = arg.split('#:')
                argsplit = argsplit[1].split(',')
                if argsplit[0].strip() == '?':
                    set_container_no_amount = True
                else:
                    numberContainers = int(argsplit[0].strip())
        #If there are no notes, and no arguments, return
        if self.Notes == None and arg == None:
            return
        #If weight is not in notes, noweight must be specified in arguments
        elif self.Notes != None:
            if 'weight' not in self.Notes:
                if 'noweight' in arg:
                    noWeight = True
                    #If noweight is specified, the number of containers must
                    #be denotes by #: followed by an integer
                    if '#:' not in arg:
                        return
                    #If this scheme is followed, set the number of containers
                    else:
                        argsplit = arg.split('#:')
                        numberContainers = int(argsplit[1].strip())
                else:
                    return
        # if weight is in the notes, extract it and set a local variable
        if noWeight == False:
            if self.Notes == None:
                weight = 0
            else:
                notesplit = self.Notes.split('weight:')
                if len(notesplit) > 1:
                    notesplit = notesplit[1].split(',')
                weight = int(notesplit[0].strip())
        # if the split is to be even, set the local variable
        if arg != None:
            if 'even' in arg:
                evenSplit = True
                # the amount to be split in this case must be denoted by
                # amt: followed by an integer representation of pounds
                if 'amt:' not in arg:
                    return
                else:
                    argsplit = arg.split('amt:')
                    argsplit = argsplit[1].split(',')
                    try:
                        amountPerContainer = int(argsplit[0].strip())
                    except:
                        set_container_no_amount = True
        # If there are a number of containers provided and no weight to be split,
        # create copies with sequencial ID's and no weight
        if numberContainers > 0 and noWeight == True:
            self.split_list = []
            for i in range(numberContainers):
                mat = material_from_db(self.ID)
                mat.ID = mat.ID+str(i)
                self.split_list.append(mat)
        elif set_container_no_amount:
            self.split_list = []
            amountPerContainer = weight/numberContainers
            for i in range(numberContainers):
                mat = material_from_db(self.ID)
                mat.ID = mat.ID+str(i)
                mat.Notes = 'weight:'+str(amountPerContainer)+'lb'
                self.split_list.append(mat)
            
        # If there are no containers specified but definite weight,
        # begin a loop of dialogues to create and fill new containers
        elif numberContainers == 0 and weight > 0:
            if amountPerContainer > 0 and evenSplit == True:
                self.split_list = []
                current_num = 1
                while weight > 0:
                    mat = material_from_db(self.ID)
                    mat.ID = mat.ID+str(current_num)
                    current_num += 1
                    if (weight - amountPerContainer) >= 0:
                        mat.Notes = 'weight:'+str(amountPerContainer)+'lb'
                        weight -= amountPerContainer
                    else:
                        remainder = abs(weight-amountPerContainer)
                        mat.Notes = 'weight:'+str(amountPerContainer - remainder)+'lb'
                        weight = 0
                    self.split_list.append(mat)
            elif set_container_no_amount == False:
                self.split_list = []
                current_num = 1
                while weight > 0:
                    mat = material_from_db(self.ID)
                    mat.ID = mat.ID + str(current_num)
                    current_num += 1
                    cweight, ok= QtGui.QInputDialog.getText(dest.getScreen('intake'),'Container:'+str(current_num),'Weight (in pounds):')
                    if ok:
                        if (weight - int(cweight) >= 0):
                            mat.Notes = 'weight:'+str(cweight)+'lb'
                            weight -= int(cweight)
                        else:
                            remainder = abs(weight - int(cweight))
                            mat.Notes = 'weight:'+str(int(cweight)-remainder)+'lb'
                            weight = 0
                        self.split_list.append(mat)
            
        #lastly, delete the temporary entry in the database
        self.delete()
        
        
    def get_split(self):
        if self.split_list == None:
            return
        else:
            return self.split_list

    def initial_intake_report(self):
        report = '(ID: '+self.ID+') ('+str(self.Notes)+')'
        return report
        
    def write(self):
        if sql.query('*','Material','WHERE ID="'+self.ID+'"'):
            sql.update('Material','Name',self.Name,'ID',self.ID)
            sql.update('Material','Form',self.Form,'ID',self.ID)
            sql.update('Material','Stage',self.Stage,'ID',self.ID)
            sql.update('Material','Source',self.Source,'ID',self.ID)
            sql.update('Material','Location',self.Location,'ID',self.ID)
            sql.update('Material','Active',self.Active,'ID',self.ID)
            sql.update('Material','Notes',self.Notes,'ID',self.ID)
            sql.update('Material','Forked_From',self.Forked_From,'ID',self.ID)
        else:
            self.Record = [self.ID,self.Name,self.Form,
                           self.Stage,self.Source,self.Location,
                           self.Notes,self.Forked_From,self.Active]
            sql.insert('Material',self.Record)
    def delete(self):
        if sql.query('*','Material','WHERE ID="'+self.ID+'"'):
            sql.delete('Material','ID="'+self.ID+'"')

def material_from_db(ID):
    contents = sql.query('*','Material','WHERE ID="'+ID+'"')[0]
    if contents:
        nID = contents[0]
        nName = contents[1]
        nForm = contents[2]
        nStage = contents[3]
        nSource = contents[4]
        nLocation = contents[5]
        nNotes = contents[6]
        nForked_From = contents[7]
        nActive = contents[8]
        
        new = material(nID,nName,nForm,nStage,nSource,nLocation,nActive,nNotes,nForked_From)
        workspace.append(new)
        return new

class message(QtGui.QMessageBox):
    def __init__(self,text,icon):
        super(message, self).__init__()
        self.setIcon(icon)
        self.setText(text)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.show()

class destinations:
    def __init__(self):
        self.screens = {}
        
    def addScreen(self,text,screen):
        self.screens.update({text:screen})
        
    def getScreen(self,text):
        return self.screens[text]

dest = destinations()
activeScreens = []

def start_fade():
    if activeScreens == []:
        dest.getScreen('MAIN').toSwitch = 'start'
        dest.getScreen('MAIN').switch()

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi(UIstem+'SDOM.ui', self)
        
        self.label.hide()
        self.toSwitch = None
        
        self.setWindowTitle('Super Dope Operations Management')
        self.showFullScreen()

        self.label.setPixmap(QtGui.QPixmap("/home/dietpi/Code/Python/oldschool/SDLabs/SDLOGO.jpg"))
        self.label.setScaledContents(True)
        
        
        self.actionCustomer_Relations.triggered.connect(lambda: self.pageOpen('cr'))
        self.actionIntake.triggered.connect(lambda: self.pageOpen('intake'))
        self.actionLab.triggered.connect(lambda: self.pageOpen('extraction'))
        self.actionFinishing.triggered.connect(lambda: self.pageOpen('finishing'))
        self.actionYield.triggered.connect(lambda: self.pageOpen('yield'))
        self.actionProduct_Management.triggered.connect(lambda: self.pageOpen('pm'))
        self.actionPackaging.triggered.connect(lambda: self.pageOpen('packaging'))
        self.actionDistillate.triggered.connect(lambda: self.pageOpen('distillate'))
        self.actionPOS.triggered.connect(lambda: self.pageOpen('pos'))
        self.actionIClick.triggered.connect(lambda: self.pageOpen('iclick'))
        self.actionLog_Access.triggered.connect(lambda: self.pageOpen('../../.logAccess/logAccess'))
        self.actionExit.triggered.connect(self.logClose_main)
        
        self.center()
        
    def logClose_main(self):
        self.toSwitch = 'quit'
        self.fadeOutPix()
        
    def fadeOutPix(self):
        self.effect = QtGui.QGraphicsOpacityEffect()
        self.label.setGraphicsEffect(self.effect)
        self.anim = QPropertyAnimation(self.effect,"opacity")
        self.fadeOut()
        self.anim.finished.connect(self.switch)
        
    def fadeInPix(self):
        self.effect = QtGui.QGraphicsOpacityEffect()
        self.label.setGraphicsEffect(self.effect)
        self.anim = QPropertyAnimation(self.effect,"opacity")
        self.fadeIn()
        self.anim.finished.connect(self.switch)
        
    def fadeIn(self):
        self.anim.setDuration(600)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        self.anim.start()
        
    def fadeOut(self):
        self.anim.setDuration(400)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        self.anim.start()
        
    def pageOpen(self,page):
        self.toSwitch = page
        self.fadeOut()
        
    def center(self):
        frameGm = self.frameGeometry()
        screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.label.move(frameGm.topLeft())
        
    def switch(self):
        if self.toSwitch == None: return
        elif self.toSwitch == 'quit': exit()
        elif self.toSwitch == 'start':
            self.toSwitch = None
            self.label.show()
            self.fadeInPix()
            return
        self.label.hide()
        switch_screen(self.toSwitch)
        activeScreens.append(self.toSwitch)
        self.toSwitch = None
            
class CR_Base(QtGui.QMainWindow):
    def __init__(self):
        super(CR_Base, self).__init__()
        uic.loadUi(UIstem+'CustomerRelations.ui', self)
        
        self.quit_button.triggered.connect(self.close)
        
        self.dragPos = QtCore.QPoint(100,100)
        
        self.actionNew.triggered.connect(self.newCustomer)
        self.actionView_Selected.triggered.connect(self.viewSelected)
        self.actionEdit_Selected.triggered.connect(self.editSelected)
        self.listWidget.itemDoubleClicked.connect(self.viewSelected)
        self.actionDelete_Selected.triggered.connect(self.deleteSelected)
        
        self.refresh()
        
    def refresh(self):
        self.listWidget.clear()
        for i in sql.query('ID','Company'):
            newi = 'COMPANY | '+i[0] + "  ---  " + sql.query('Name','Company','WHERE ID="'+i[0]+'"')[0][0]
            self.listWidget.addItem(newi)
        for i in sql.query('ID','Contact'):
            newi = 'CONTACT | '+i[0] + "  ---  " + sql.query('Name','Contact','WHERE ID="'+i[0]+'"')[0][0]
            self.listWidget.addItem(newi)
        
    def newCustomer(self):
        self.New = CR_New()
        self.New.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.New.show()
        
    def editSelected(self):
        self.Edit = CR_Edit()
        self.Edit.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.Edit.show()
        
    def deleteSelected(self):
        self.delwin = message('Press ok to delete '+str(self.listWidget.currentItem().text()),QtGui.QMessageBox.Critical)
        self.delwin.buttonClicked.connect(self.confirmedDeletion)
        
    def confirmedDeletion(self):
        current = str(self.listWidget.currentItem().text())
        current = current.split(' --- ')
        current = current[0].split(' | ')
        if sql.query('ID',current[0].strip(),'WHERE id="'+current[1].strip()+'"')[0] != []:
            sql.delete(current[0].strip(),'id="'+current[1].strip()+'"')
        self.refresh()
        self.delwin2 = message('Press ok to save change ',QtGui.QMessageBox.Information)
        self.delwin2.buttonClicked.connect(lambda x: sql.connection.commit())
        
    def viewSelected(self):
        self.View = CR_View()
        self.View.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        current = str(self.listWidget.currentItem().text())
        current = current.split(' --- ')
        current = current[0].split(' | ')
        results = sql.query('*',current[0].strip(),'WHERE id="'+current[1].strip()+'"')[0]
        self.View.labelID.setText(results[0])
        
        self.View.labelName.setText(results[1])
        if current[0] == 'CONTACT':
            self.View.labelAffiliation.setText(results[5])
        else:
            self.View.labelAffiliation1.hide()
            self.View.labelAffiliation.hide()
        self.View.labelContactNum.setText(results[2])
        self.View.labelEmail.setText(results[3])
        self.View.labelAddress.setText(results[4])
        if current[0] == 'COMPANY':
            self.View.labelLicense.setText(results[5])
        else:
            self.View.labelLicense.hide()
            self.View.label_5.hide()
        if current[0] == 'CONTACT':
            self.View.labelNotes.setText(results[6])
        self.View.show()
        
    def close(self):
        self.hide()
        activeScreens.remove('cr')
        start_fade()
        
    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.RightButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()
        

class CR_New(QtGui.QDialog):
    def __init__(self):
        super(CR_New, self).__init__()
        uic.loadUi(UIstem+'customerNew.ui', self)
        
        self.buttonBox.accepted.connect(self.okClick)
        self.buttonBox.rejected.connect(self.cancelClick)
        
    def okClick(self):
        has_company = False
        has_contact = False
        has_num = False
        has_email = False
        has_address = False
        has_license = False
        has_notes = False
        
        company_value = str(self.lineCompany.displayText())
        if company_value != '': has_company = True
        contact_value = str(self.lineContactName.displayText())
        if contact_value != '': has_contact = True
        num_value = str(self.lineContactNum.displayText())
        if num_value != '': has_num = True
        email_value = str(self.lineEmail.displayText())
        if email_value != '': has_email = True
        address_value = str(self.lineAddress.displayText())
        if address_value != '': has_address = True
        license_value = str(self.lineLicenseNum.displayText())
        if license_value != '': has_license = True
        notes_value = str(self.textNoteBox.toPlainText())
        if notes_value != '': has_notes = True
        
        will_target_company = False
        will_target_contact = False
        will_set_affiliation = False
        
        # If company, but no contact, add company
        # If contact, but no company, add contact
        # If contact, and company, add company as affiliation to contact
        # If no company, or contact, warning message
        if has_company == True:
            if has_contact == True:
                will_set_affiliation = True
                will_target_contact = True
            else:
                will_target_company = True
        else:
            if has_contact == True:
                will_target_contact = True
            else:
                self.warning = message("Must enter Company or Contact!",QtGui.QMessageBox.Warning)
                return
                
        data_values = []
        
        if will_target_company == True:
            csplit = company_value.split(' ')
            ID = company_value[:3]
            ID = self.idCheck(ID)
            data_values.append(ID)
            data_values.append(company_value)
            if has_num:
                data_values.append(num_value)
            else: data_values.append('No Number')
            if has_email:
                data_values.append(email_value)
            else: data_values.append('No Email')
            if has_address:
                data_values.append(address_value)
            else: data_values.append('No Address')
            if has_license:
                data_values.append(license_value)
            else: data_values.append('No License')
            
            sql.insert('Company',data_values)
            sql.connection.commit()
            
        if will_target_contact == True:
            ID = contact_value[:2]
            ID = self.idCheck(ID,contact=True)
            data_values.append(ID)
            data_values.append(contact_value)
            if has_num:
                data_values.append(num_value)
            else: data_values.append('No Number')
            if has_email:
                data_values.append(email_value)
            else: data_values.append('No Email')
            if has_address:
                data_values.append(address_value)
            else: data_values.append('No Address')
            if will_set_affiliation:
                data_values.append(company_value)
            else: data_values.append('No Affiliation')
            if has_notes:
                data_values.append(notes_value)
            else: data_values.append('No Notes')
            
            sql.insert('Contact',data_values)
            sql.connection.commit()
            
        dest.getScreen('cr').refresh()
        self.hide()
        
    def idCheck(self,ID,contact=False):
        if contact == True:
            if sql.query('*','Contact','WHERE ID = "'+str(ID)+'"') != []:
                ID += '1'
                return self.idCheck(ID,contact=True)
            else:
                return ID
        if sql.query('*','Company','WHERE ID = "'+str(ID)+'"') != []:
                ID += '1'
                return self.idCheck(ID)
        else:
            return ID
        
    def cancelClick(self):
        self.hide()
        self.lineCompany.clear()
        self.lineContactName.clear()
        self.lineContactNum.clear()
        self.lineEmail.clear()
        self.lineAddress.clear()
        self.lineLicenseNum.clear()
        self.textNoteBox.clear()
        if self.pushBuyer.isChecked(): self.pushBuyer.toggle()
        if self.pushSupplier.isChecked(): self.pushSupplier.toggle()

class CR_Edit(QtGui.QDialog):
    def __init__(self):
        super(CR_Edit, self).__init__()
        uic.loadUi(UIstem+'CustomerEdit.ui', self)
        
class CR_View(QtGui.QDialog):
    def __init__(self):
        super(CR_View, self).__init__()
        uic.loadUi(UIstem+'CustomerView.ui', self)

class Intake_Base(QtGui.QMainWindow):
    def __init__(self):
        super(Intake_Base, self).__init__()
        uic.loadUi(UIstem+'intakeMain.ui', self)
        
        self.quit_button.triggered.connect(self.close)
        
        self.newBag.triggered.connect(self.intakeBegin)
        self.actionPost_Test.triggered.connect(self.intakePost)
        
        # intake subwindows:
        '''self.intake_initial = Intake_Initial()
        self.intake_initial_weight = Intake_Initial_Weight()
        self.intake_post = Intake_Post()'''
        
        self.dragPos = QtCore.QPoint(100,100)
        
    def intakeBegin(self):
        self.initial = Intake_Initial()
        self.initial.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.initial.show() 
        self.hide()
         
        
    def intakePost(self):
        self.post = Intake_Post()
        self.post.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.post.show() 
    
    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.RightButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()
        
    def close(self):
        self.hide()
        activeScreens.remove('intake')
        start_fade()
        
        
class Intake_Initial(QtGui.QDialog):
    def __init__(self):
        super(Intake_Initial, self).__init__()
        uic.loadUi(UIstem+'intakeInitial.ui',self)
        
        # Handle Ok and Cancel buttons
        self.buttonBox.accepted.connect(self.okClick)
        self.buttonBox.rejected.connect(self.cancelClick)
        
        self.owner_value = None
        self.flavor_value = None
        self.bagNum_value = None
        self.location_value = None
        
        self.refresh()
    
    def okClick(self):
        self.owner_value = str(self.dropOwner.currentText())
        self.flavor_value = str(self.editFlavor.displayText())
        self.bagNum_value = str(self.editNumBag.displayText())
        self.location_value = str(self.dropLocation.currentText())
        self.ID_value = self.owner_value.split(' --- ')[0].split(' | ')[1].strip()
        
        self.initial_weight = Intake_Initial_Weight()
        # pass self along so the values can be snatched by the next screen
        self.initial_weight.ref = self
        
        
        self.hide()
        self.editFlavor.clear()
        self.editNumBag.clear()
        self.dropLocation.clear()
        self.dropOwner.clear()
        
        self.initial_weight.refresh()
    
    def cancelClick(self):
        self.editFlavor.clear()
        self.editNumBag.clear()
        self.dropLocation.clear()
        self.dropOwner.clear()
        self.hide()
        dest.getScreen('intake').show()
        self.refresh()
        
    def refresh(self):
        self.dropOwner.clear()
        for i in sql.query('ID','Company'):
            newi = 'Company | '+i[0] + "  ---  " + sql.query('Name','Company','WHERE ID="'+i[0]+'"')[0][0]
            self.dropOwner.addItem(newi)
        for i in sql.query('ID','Contact'):
            newi = 'Contact | '+i[0] + "  ---  " + sql.query('Name','Contact','WHERE ID="'+i[0]+'"')[0][0]
            self.dropOwner.addItem(newi)
        for i in sql.query('ID','Location'):
            newi = 'Location | '+i[0] + "  ---  " + sql.query('Name','Location','WHERE ID="'+i[0]+'"')[0][0]
            self.dropLocation.addItem(newi)
        
        
        
class Intake_Initial_Weight(QtGui.QDialog):
    def __init__(self):
        super(Intake_Initial_Weight, self).__init__()
        uic.loadUi(UIstem+'intakeInitialWeight.ui',self)
        
        self.ref = Intake_Initial()
        
    def refresh(self):
        self.labelOwnerFlavor.setText(self.ref.owner_value + ' -> ' + self.ref.flavor_value)
        self.labelSerial.setText(self.idCheck()+"/"+current_date+"/"+self.ref.flavor_value)
        
        # Boolean to denote if the round will be split from bags into totes/smaller bags
        self.will_be_split = False
        # Boolean to denote if the weight has been entered yet or not. 
        # If not, flag resulting material items to be filled out upon reminder.
        self.has_weight = False
        self.current_weight = 0
        # If the round will be split, this will hold the number of new containers
        self.container_number = 0
        # If the containers will be split, and there is weight recorded...
        # Boolean deciding if the split will be even across new containers.
        self.even_split = False
        pounds_per_container = 0
        by_weight = False
        by_number = False
        
        weight, ok= QtGui.QInputDialog.getText(self,self.ref.flavor_value,'Weight(lb): \n*Enter 0 for unknown\nor to enter later...')
        if ok:
            # Ask if the bags are being split into bins.
            split_result, ok= QtGui.QInputDialog.getText(self,'Split?','Will these bags be split into smaller/different containers?(YES/NO)')
            if ok:
                # If the bags are to be split. How many containers will they be split into?
                if 'Y' in str(split_result).upper():
                    self.will_be_split = True
                    even_split, ok= QtGui.QInputDialog.getText(self,'Even?','Will the split be even across containers?')
                    if ok:
                        if 'Y' in str(even_split).upper():
                            self.even_split = True
                        else:
                            container_number, ok= QtGui.QInputDialog.getText(self,'How many?','How many of those containers are there? \nType ? for unknown')
                            if ok:
                                if container_number == '?': container_number = 0
                                self.container_number = int(container_number)
                else:
                    pass
            # If weight == 0, 
            if int(weight) == 0:
                pass
            else: 
                self.has_weight = True
                self.current_weight = int(weight)
                
            # Now that it has been determined, whether weight is recorded and what that weight is, and whether the
            # rounds will be split up and how many containers that will be divided into,
            # proceed to lay out the data in the list widget.
            entries = []
            rID = self.ref.ID_value+'/'+current_date[:-5]+'/'+self.ref.flavor_value[:3]
            rName = self.ref.flavor_value
            rForm = 'Trim'
            if self.will_be_split:
                rForm += 'tote'
                
            rStage = 'Intake'
            rSource = self.ref.owner_value
            rLocation = self.ref.location_value
            rActive = True
            rNotes = None
            if self.has_weight:
                rNotes = "weight:"+str(self.current_weight)
            
            self.root_mat = material(rID,rName,rForm,rStage,rSource,rLocation,rActive,Notes=rNotes)
            
            
            if self.will_be_split:
                if self.even_split:
                    if self.container_number == 0:
                        howmuch, ok= QtGui.QInputDialog.getText(self,'How Much?','How many pounds per container?\n Type ? for unknown')
                        if ok:
                            if howmuch == '?':
                                pounds_per_container = '?'
                                howmany, ok= QtGui.QInputDialog.getText(self,'How Many?','How many containers?')
                                if ok:
                                    self.container_number = int(howmany)
                            else:
                                pounds_per_container = int(howmuch)
                            
                    self.root_mat.split('even,amt:'+str(pounds_per_container)+',#:'+str(self.container_number))
                else:
                    self.root_mat.split('#:'+str(self.container_number))
            else:
                self.root_mat.write()
                self.root_mat.split_list = []
                for item in range(int(self.ref.bagNum_value)):
                    mat = material_from_db(self.root_mat.ID)
                    mat.ID = mat.ID + str(item+1)
                    self.root_mat.split_list.append(mat)
                    
            self.mat_list = self.root_mat.get_split()
            
            for item in self.mat_list:
                self.listContainer.addItem(item.initial_intake_report())
            
            
            self.show()
                
        else:
            dest.getScreen('intake').show()
                
            
                
        
    def idCheck(self):
        if sql.query('*','Material','WHERE ID = "'+str(self.ref.ID_value)+'"') != []:
                self.ref.ID_value += '1'
                return self.idCheck(ID)
        else:
            return self.ref.ID_value
        
        
class Intake_Post (QtGui.QDialog):
    def __init__(self):
        super(Intake_Post, self).__init__()
        uic.loadUi(UIstem+'intakePost.ui',self)

class Extraction_Base(QtGui.QMainWindow):
    def __init__(self):
        global OpenTotes
        super(Extraction_Base, self).__init__()
        uic.loadUi(UIstem+'runMain.ui', self)
        
        self.quit_button.triggered.connect(self.close)
        self.startRun.triggered.connect(self.start)
        
        self.dragPos = QtCore.QPoint(100,100)
        
    def start(self):
        self.prompt = Extraction_RunPrompt()
        self.prompt.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.prompt.show() 
        
    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.RightButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()
        
    def close(self):
        self.hide()
        activeScreens.remove('extraction')
        start_fade()
        
class Extraction_RunPrompt(QtGui.QDialog):
    def __init__(self):
        global OpenTotes,CurrentNum
        super(Extraction_RunPrompt, self).__init__()
        uic.loadUi(UIstem+'runPrompt.ui', self)
        
class Extraction_RunView(QtGui.QDialog):
    def __init__(self,run):
        global OpenTotes,CurrentNum
        super(Extraction_RunView, self).__init__()
        uic.loadUi(UIstem+'runView.ui', self)
        
class Finishing_Base(QtGui.QMainWindow):
    def __init__(self):
        super(Finishing_Base, self).__init__()
        uic.loadUi(UIstem+'finishingMain.ui', self)
        
        self.quit_button.triggered.connect(self.close)
        
        self.dragPos = QtCore.QPoint(100,100)
        
    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.RightButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()
        
    def close(self):
        self.hide()
        activeScreens.remove('finishing')
        start_fade()
        
class Yield_Base(QtGui.QMainWindow):
    def __init__(self):
        super(Yield_Base, self).__init__()
        uic.loadUi(UIstem+'yieldMain.ui', self)
        
        self.quit_button.triggered.connect(self.close)
        
        self.dragPos = QtCore.QPoint(100,100)
        
    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.RightButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()
        
    def close(self):
        self.hide()
        activeScreens.remove('yield')
        start_fade()

class Yield_Pop(QtGui.QDialog):
    def __init__(self):
        super(Yield_Pop, self).__init__()
        uic.loadUi(cl.UIstem+'yieldPOP.ui', self)
        
class PM_Base(QtGui.QMainWindow):
    def __init__(self):
        super(PM_Base, self).__init__()
        uic.loadUi(UIstem+'productManagement.ui', self)
        
        self.quit_button.triggered.connect(self.close)
        
        self.dragPos = QtCore.QPoint(100,100)
        
    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.RightButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()
        
    def close(self):
        self.hide()
        activeScreens.remove('pm')
        start_fade()

class PM_View(QtGui.QDialog):
    def __init__(self):
        super(PM_View, self).__init__()
        uic.loadUi(UIstem+'productManagementView.ui', self)
        
class Packaging_Base(QtGui.QMainWindow):
    def __init__(self):
        super(Packaging_Base, self).__init__()
        uic.loadUi(UIstem+'packagingMain.ui', self)
        
        self.quit_button.triggered.connect(self.close)
        
        self.dragPos = QtCore.QPoint(100,100)
        
    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.RightButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()
        
    def close(self):
        self.hide()
        activeScreens.remove('packaging')
        start_fade()
        
class Packaging_Make(QtGui.QDialog):
    def __init__(self):
        super(Packaging_Make, self).__init__()
        uic.loadUi(UIstem+'packagingMake.ui',self)
        
class Packaging_Select(QtGui.QDialog):
    def __init__(self):
        super(Packaging_Select, self).__init__()
        uic.loadUi(UIstem+'packagingSelect.ui',self)
        
class POS_Base(QtGui.QMainWindow):
    def __init__(self):
        super(POS_Base, self).__init__()
        uic.loadUi(UIstem+'posMain.ui', self)
        
        self.quit_button.triggered.connect(self.close)
        
        self.dragPos = QtCore.QPoint(100,100)
        
    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.RightButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()
        
    def close(self):
        self.hide()
        activeScreens.remove('pos')
        start_fade()
        
class POS_Pricing(QtGui.QDialog):
    def __init__(self):
        super(POS_Pricing, self).__init__()
        uic.loadUi(UIstem+'posPricing.ui', self)
        
class POS_Review(QtGui.QDialog):
    def __init__(self):
        super(POS_Review, self).__init__()
        uic.loadUi(UIstem+'posReview.ui', self)
        
class POS_SoldTo(QtGui.QDialog):
    def __init__(self):
        super(POS_SoldTo, self).__init__()
        uic.loadUi(UIstem+'posSoldTo.ui', self)
        


import atexit
atexit.register(logClose)
