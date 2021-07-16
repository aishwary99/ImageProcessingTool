import numpy
import sys
import cv2
import math
import numpy as np
import os.path
from os import path
from PyQt5.QtCore import Qt,QThread,QObject,pyqtSignal,QStandardPaths
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtGui import *
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PIL import Image, ImageFont, ImageDraw  
from threading import Timer
import time

def convertToRGB(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

class DataModel():
    def __init__(self,width,height):
        self.width=width
        self.height=height
    
    def getWidth(self):
        return self.width
    
    def getHeight(self):
        return self.height

class Worker(QThread):
    signal=pyqtSignal("PyQt_PyObject")
    def setTmApplication(self,tmApplication):
        self.tmApplication=tmApplication
    
    def setOperation(self,operation):
        self.operation=operation
    
    def setRadius(self,radius):
        self.radius=radius
    
    def setOperationString(self,operationString):
        self.operationString=operationString

    def run(self):
        if self.operation==0:
            pass
        elif self.operation==1:
            self.tmApplication.imageProcessor.performGrayScale()
        elif self.operation==2:
            self.tmApplication.imageProcessor.performBrightnessOperation(self.tmApplication.brightnessFactor)
        elif self.operation==3:
            self.tmApplication.imageProcessor.performContrastOperation(self.tmApplication.contrastFactor)
        elif self.operation==4:
            self.tmApplication.imageProcessor.getPreviewForCrop(self.tmApplication.startingPreviewX,self.tmApplication.startingPreviewY,self.tmApplication.endingPreviewX,self.tmApplication.endingPreviewY)
        elif self.operation==5:
            self.tmApplication.imageProcessor.performCrop(self.tmApplication.startingPreviewX,self.tmApplication.startingPreviewY,self.tmApplication.endingPreviewX,self.tmApplication.endingPreviewY)
        elif self.operation==6:
            #horizontal flip
            self.tmApplication.imageProcessor.performHorizontalFlip()
        elif self.operation==7:
            #vertical flip
            self.tmApplication.imageProcessor.performVerticalFlip()
        elif self.operation==8:
            #rotation clockwise 90
            self.tmApplication.imageProcessor.performClockwise()
        elif self.operation==9:
            #rotation anticlockwise 90
            self.tmApplication.imageProcessor.performAnticlockwise()
        elif self.operation==10:
            #rotation 180
            self.tmApplication.imageProcessor.perform180()
        elif self.operation==11:
            #overlay
            self.tmApplication.imageProcessor.performOverlay(self.tmApplication.startingOverlayX,self.tmApplication.startingOverlayY)
        elif self.operation==12:
            #resize
            self.tmApplication.imageProcessor.performResize(self.tmApplication.destHeight,self.tmApplication.destWidth)
        elif self.operation==13:
            #gaussian blur
            self.tmApplication.imageProcessor.performGuassianBlur(self.radius)
        elif self.operation==14:
            #vertical motion blur
            self.tmApplication.imageProcessor.performVerticalMotionBlur(self.radius)
        elif self.operation==15:
            #horizontal motion blur
            self.tmApplication.imageProcessor.performHorizontalMotionBlur(self.radius)
        elif self.operation==16:
            #box blur
            self.tmApplication.imageProcessor.performBoxBlur()
        elif self.operation==17:
            #invert
            self.tmApplication.imageProcessor.performInvert()
        elif self.operation==18:
            #sharpen
            self.tmApplication.imageProcessor.performSharpening()
        elif self.operation==19:
            #unsharp
            self.tmApplication.imageProcessor.performUnsharpening()
        elif self.operation==20:
            #laplace
            self.tmApplication.imageProcessor.performLaplace()
        elif self.operation==21:
            #put text on image
            self.tmApplication.imageProcessor.performTextOperation(self.tmApplication.textOnImage,self.tmApplication.fontPath,self.tmApplication.fontColorCode,self.tmApplication.fontSize,self.tmApplication.textX,self.tmApplication.textY)
        elif self.operation==22:
            #perform zoom in
            self.tmApplication.imageProcessor.performZoomIn()
        elif self.operation==23:
            #perform zoom out
            self.tmApplication.imageProcessor.performZoomOut()
        elif self.operation==24:
            #watermark image operation
            self.tmApplication.imageProcessor.performImageWatermark(self.tmApplication.watermarkImagePath,self.tmApplication.watermarkImageOpacity,self.tmApplication.watermarkImageCoordinates)
        elif self.operation==25:
            #watermark text operation
            self.tmApplication.imageProcessor.performTextWatermark(self.tmApplication.watermarkText,self.tmApplication.watermarkTextSize,self.tmApplication.watermarkTextThickness,self.tmApplication.watermarkTextOpacity,self.tmApplication.watermarkTextCoordinates)
        elif self.operation==26:
            #normal border 
            self.tmApplication.imageProcessor.performNormalBorderOperation(self.operationString)
        elif self.operation==27:
            #replicate border
            self.tmApplication.imageProcessor.performReplicateBorderOperation(self.operationString)
        self.signal.emit("Completed")

class TMApplication(QMainWindow,QWidget):
    def __init__(self,model,parent=None):
        super().__init__(parent)
        self.brightnessFactor=0
        self.contrastFactor=0
        self.worker=Worker()
        self.images={}
        self.model=model
        self.imageProcessor=self.ImageProcessor(self)
        self.setWindowTitle("Pixi")
        self.setFixedSize(self.model.getWidth(),self.model.getHeight())
        self.setWindowIcon(QtGui.QIcon("img/logo_black.png"))
        self.createMenuBar()
        self.createToolBar()
        self.createStatusBar()
        self.loadFonts()
        self.loadLogFiles()
        self.setFrameGeometry()

    def setFrameGeometry(self):
        frameGeometry=self.frameGeometry()
        centerPoint=QDesktopWidget().availableGeometry().center()
        frameGeometry.moveCenter(centerPoint)
        self.move(frameGeometry.topLeft())
    
    def loadLogFiles(self):
        self.logFiles=list()
        self.logFiles.append("Loading font database...")
        self.logFiles.append("Loading menu...")
        self.logFiles.append("Loading toolbar...")
        self.logFiles.append("Loading image processor...")
        self.logFiles.append("Loading status bar...")
        self.logFiles.append("Loading log files...")
        self.logFiles.append("Loading cache...")
        self.logFiles.append("Loading worker thread...")
        self.logFiles.append("Loading panels...")
        self.logFiles.append("Initializing UI...")


    def loadFonts(self):
        self.family_to_path=dict()
        self.accounted=list()
        self.unloadable=list()
        font_paths=QStandardPaths.standardLocations(QStandardPaths.FontsLocation)
        font_database=QFontDatabase()
        for path in font_paths:
            for font in os.listdir(path):
                font_path=os.path.join(path,font)
                index=font_database.addApplicationFont(font_path)
                if index<0: self.unloadable.append(font_path)
                font_names=font_database.applicationFontFamilies(index)
                for font_name in font_names:
                    if font_name in self.family_to_path:
                        self.accounted.append((font_name,font_path))
                    else:
                        self.family_to_path[font_name]=font_path

    def checkPreviousStuff(self):
        if path.isfile("temp.png"): os.remove("temp.png")
        elif path.isfile("temp.jpg"): os.remove("temp.jpg")
    
    def updateStatusBar(self):
        msg=self.images["status"]
        self.statusBar.showMessage(msg,3000)
    
    def updateImageOnUI(self):
        imagePath=self.images["filterImageName"]
        if imagePath=="": imagePath=self.images["path"]
        imageName=self.images["name"]
        imageResolution=str(self.images["height"])+"x"+str(self.images["width"])
        imageSize=str(self.images["size"])+" MB"
        
        #label for image
        self.lx1=1
        self.ly1=61
        self.lx2=828
        self.ly2=508
        self.rx1=self.lx1+1+self.lx2+219
        self.ry1=self.ly1
        self.rx2=199
        self.ry2=18

        self.leftPanel=QLabel()
        self.leftPanel.setPixmap(QPixmap(imagePath))
        #self.leftPanel.setGeometry(self.lx1,self.ly1,self.lx2,self.ly2)
        #self.leftPanel.setStyleSheet("border: 1px solid black; width:200px;")

        self.scrollArea=QScrollArea()
        self.widget=QWidget()
        self.boxLayout=QVBoxLayout()


        self.boxLayout.addWidget(self.leftPanel)
        self.widget.setLayout(self.boxLayout)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.widget)
        self.scrollArea.setMaximumWidth(1046)
        self.setCentralWidget(self.scrollArea)


        self.rightPanel1=QLabel(self)
        self.rightPanel1.setGeometry(self.rx1,self.ry1,self.rx2,self.ry2)
        self.rightPanel1.setText("Image Details")
        self.rightPanel1.setAlignment(QtCore.Qt.AlignCenter) 
        self.rightPanel1.setStyleSheet("background-color:white;")
        self.rightPanel1.show()
        
        self.rightPanel1=QLabel(self)
        self.rightPanel1.setGeometry(self.rx1,self.ry1+18,self.rx2,self.ry2)
        self.rightPanel1.setAlignment(QtCore.Qt.AlignLeft) 
        self.rightPanel1.setStyleSheet("background-color:white; padding-left:10px;")
        self.rightPanel1.show()

        self.rightPanel1=QLabel(self)
        self.rightPanel1.setGeometry(self.rx1,self.ry1+18+18,self.rx2,self.ry2)
        self.rightPanel1.setText("File: "+imageName)
        self.rightPanel1.setAlignment(QtCore.Qt.AlignLeft) 
        self.rightPanel1.setStyleSheet("background-color:white; padding-left:10px;")
        self.rightPanel1.show()
        
        self.rightPanel1=QLabel(self)
        self.rightPanel1.setGeometry(self.rx1,self.ry1+18+18+18,self.rx2,self.ry2)
        self.rightPanel1.setText("Resolution: "+imageResolution)
        self.rightPanel1.setAlignment(QtCore.Qt.AlignLeft) 
        self.rightPanel1.setStyleSheet("background-color:white; padding-left:10px;")
        self.rightPanel1.show()
        
        self.rightPanel1=QLabel(self)
        self.rightPanel1.setGeometry(self.rx1,self.ry1+18+18+18+18,self.rx2,self.ry2)
        self.rightPanel1.setText("Size: "+imageSize)
        self.rightPanel1.setAlignment(QtCore.Qt.AlignLeft) 
        self.rightPanel1.setStyleSheet("background-color:white; padding-left:10px;")
        self.rightPanel1.show()

        self.updateStacks()
    
    def updateStacks(self):
        if len(self.images["undoStack"])>1:
            self.undoAct.setEnabled(True)
        else:
            self.undoAct.setEnabled(False)
        
        if len(self.images["redoStack"])>0:
            self.redoAct.setEnabled(True)
        else:
            self.redoAct.setEnabled(False)

    def showFontSelectorDialog(self):
        font,ok=QFontDialog.getFont()
        if ok:
            fontDetails=font.toString().split(',')
            self.fontName=fontDetails[0]
            self.fontSize=fontDetails[1]
            self.fontType=fontDetails[-1]
            if len(self.fontName)>15:
                self.fontName=self.fontName[:15]
            self.textPanelFontButton.setText(self.fontName)      
            self.textPanelFontSizeLabel.setText(self.fontSize)
            try:
                self.fontPath=self.family_to_path[self.fontName]
            except:
                errorMessage=QtWidgets.QErrorMessage(self)
                errorMessage.showMessage(f"The specified font: {self.fontName} is not available !")
                errorMessage.setWindowTitle(f"Font unavailable")
    
    def showColorSelectorDialog(self):
        color=QColorDialog.getColor()
        if color.isValid():
            self.fontColorCode=color.name()
            self.textPanelColorButton.setText(self.fontColorCode)

    def updateTextPanelParameters(self):
        self.textOnImage=self.textPanelTextArea.text()
        self.textX=self.textPanelXCoordinate.text()
        self.textY=self.textPanelYCoordinate.text()
        if len(self.textX)>0 and len(self.textY)>0: 
            self.textX=int(self.textX)
            self.textY=int(self.textY)

    def applyText(self):
        self.worker.setTmApplication(self)
        self.worker.setOperation(21)
        self.worker.signal.connect(self.taskFinished)
        self.worker.start()
        self.showLoader()

    def setOpacitySliderValue(self,sliderNo):
        if sliderNo==1:
            opacitySliderValue=str(self.watermarkPanelImageOpacitySlider.value())
            self.watermarkPanelImageOpacitySliderValueLabel.setText(opacitySliderValue)
        else:
            opacitySliderValue=str(self.watermarkPanelTextOpacitySlider.value())
            self.watermarkPanelTextOpacitySliderValueLabel.setText(opacitySliderValue)

    def showWatermarkPanel(self):
        self.watermarkImagePath=""
        self.watermarkPanelImageRadioButton.setChecked(True)
        self.watermarkPanelTitle.show()
        self.watermarkPanelImageRadioButton.show()
        self.watermarkPanelTextRadioButton.show()
        self.watermarkPanelImageLabel.show()
        self.watermarkPanelImageButton.show()
        self.watermarkPanelXImageTitleLabel.show()
        self.watermarkPanelXImageTextArea.show()
        self.watermarkPanelYImageTitleLabel.show()
        self.watermarkPanelYImageTextArea.show()
        self.watermarkPanelImageOpacityPanel.show()
        self.watermarkPanelImageOpacitySlider.show()
        self.watermarkPanelImageOpacitySliderValueLabel.show()
        self.watermarkPanelImageOKButton.show()
        self.watermarkPanelImageCloseButton.show()
    
    def hideWatermarkPanel(self):
        self.watermarkPanelTitle.hide()
        self.watermarkPanelImageRadioButton.hide()
        self.watermarkPanelTextRadioButton.hide()
        self.hideWatermarkImagePanel()
        self.hideWatermarkTextPanel()
        
    
    def showWatermarkImagePanel(self):
        self.hideWatermarkTextPanel()
        self.watermarkPanelImageRadioButton.show()
        self.watermarkPanelTextRadioButton.show()
        self.watermarkPanelImageLabel.show()
        self.watermarkPanelImageButton.show()
        self.watermarkPanelXImageTitleLabel.show()
        self.watermarkPanelXImageTextArea.show()
        self.watermarkPanelYImageTitleLabel.show()
        self.watermarkPanelYImageTextArea.show()
        self.watermarkPanelImageOpacityPanel.show()
        self.watermarkPanelImageOpacitySlider.show()
        self.watermarkPanelImageOpacitySliderValueLabel.show()
        self.watermarkPanelImageOKButton.show()
        self.watermarkPanelImageCloseButton.show()
    
    def hideWatermarkImagePanel(self):
        self.watermarkPanelImageLabel.hide()
        self.watermarkPanelImageButton.hide()
        self.watermarkPanelImageButton.setText("Choose...")
        self.watermarkPanelXImageTitleLabel.hide()
        self.watermarkPanelXImageTextArea.hide()
        self.watermarkPanelXImageTextArea.setText("0")
        self.watermarkPanelYImageTitleLabel.hide()
        self.watermarkPanelYImageTextArea.hide()
        self.watermarkPanelYImageTextArea.setText("0")
        self.watermarkPanelImageOpacityPanel.hide()
        self.watermarkPanelImageOpacitySlider.hide()
        self.watermarkPanelImageOpacitySlider.setFocusPolicy(Qt.NoFocus)
        self.watermarkPanelImageOpacitySlider.setTickPosition(QSlider.NoTicks)
        self.watermarkPanelImageOpacitySlider.setTickInterval(10)
        self.watermarkPanelImageOpacitySlider.setSingleStep(1)
        self.watermarkPanelImageOpacitySlider.setValue(50)
        self.watermarkPanelImageOpacitySliderValueLabel.hide()
        self.watermarkPanelImageOpacitySliderValueLabel.setText("50")
        self.watermarkPanelImageOKButton.hide()
        self.watermarkPanelImageCloseButton.hide()

    def hideWatermarkTextPanel(self):
        self.watermarkPanelTextLabel.hide()
        self.watermarkPanelTextButton.hide()
        self.watermarkPanelTextButton.setText("")
        self.watermarkPanelXTextTitleLabel.hide()
        self.watermarkPanelXTextTextArea.hide()
        self.watermarkPanelXTextTextArea.setText("0")
        self.watermarkPanelYTextTitleLabel.hide()
        self.watermarkPanelYTextTextArea.hide()
        self.watermarkPanelYTextTextArea.setText("0")
        self.watermarkPanelTextThicknessLabel.hide()
        self.watermarkPanelTextThicknessTextArea.hide()
        self.watermarkPanelTextThicknessTextArea.setText("0")
        self.watermarkPanelTextSizeLabel.hide()
        self.watermarkPanelTextSizeTextArea.hide()
        self.watermarkPanelTextSizeTextArea.setText("0")
        self.watermarkPanelTextOpacityPanel.hide()
        self.watermarkPanelTextOpacitySlider.hide()
        self.watermarkPanelTextOpacitySlider.setFocusPolicy(Qt.NoFocus)
        self.watermarkPanelTextOpacitySlider.setTickPosition(QSlider.NoTicks)
        self.watermarkPanelTextOpacitySlider.setTickInterval(10)
        self.watermarkPanelTextOpacitySlider.setSingleStep(1)
        self.watermarkPanelTextOpacitySlider.setValue(50)
        self.watermarkPanelTextOpacitySliderValueLabel.hide()
        self.watermarkPanelTextOKButton.hide()
        self.watermarkPanelTextCloseButton.hide()


    def showWatermarkTextPanel(self):
        self.hideWatermarkImagePanel()
        self.watermarkPanelTextLabel.show()
        self.watermarkPanelTextButton.show()
        self.watermarkPanelXTextTitleLabel.show()
        self.watermarkPanelXTextTextArea.show()
        self.watermarkPanelYTextTitleLabel.show()
        self.watermarkPanelYTextTextArea.show()
        self.watermarkPanelTextThicknessLabel.show()
        self.watermarkPanelTextThicknessTextArea.show()
        self.watermarkPanelTextSizeLabel.show()
        self.watermarkPanelTextSizeTextArea.show()
        self.watermarkPanelTextOpacityPanel.show()
        self.watermarkPanelTextOpacitySlider.show()
        self.watermarkPanelTextOpacitySliderValueLabel.show()
        self.watermarkPanelTextOKButton.show()
        self.watermarkPanelTextCloseButton.show()

    
    def openWatermarkImageChooser(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filePath, _ = QFileDialog.getOpenFileName(self,"Choose an image", "","JPG (*.jpg);;PNG (*.png);;JPEG (*.jpeg);", options=options)
        fileName=""
        if filePath:
            self.watermarkImagePath=filePath
            fileName=filePath[filePath.rfind("/")+1:]
            if len(fileName)>10:
                fn=fileName[:8]+"..."    
                self.watermarkPanelImageButton.setText(fn)
            else: self.watermarkPanelImageButton.setText(fileName)

    def validateWatermarkImageParameters(self):
        hasError=False
        x=self.watermarkPanelXImageTextArea.text()
        y=self.watermarkPanelYImageTextArea.text()
        errorMessage=""
        errorMessageDialog=QtWidgets.QErrorMessage(self)
        if len(self.watermarkImagePath)==0:
            hasError=True
            errorMessage+="Image not selected. \r\n"
        if len(x)==0 or int(x)==0:
            errorMessage+="Invalid x-coordinte. \r\n"
            hasError=True
        if len(y)==0 or int(y)==0:
            errorMessage+="Invalid y-coordinte. \r\n"
            hasError=True
        if hasError:
            errorMessageDialog.showMessage(errorMessage)
            errorMessageDialog.setWindowTitle("Error !")
            errorMessageDialog.show()
        else: self.applyImageWatermark()
    
    def applyImageWatermark(self):
        x=int(self.watermarkPanelXImageTextArea.text())
        y=int(self.watermarkPanelYImageTextArea.text())
        self.watermarkImageCoordinates=x,y
        self.watermarkImageOpacity=int(self.watermarkPanelImageOpacitySliderValueLabel.text())
        self.worker.setTmApplication(self)
        self.worker.setOperation(24)
        self.worker.signal.connect(self.taskFinished)
        self.worker.start()
        self.showLoader()
    
    def applyTextWatermark(self):
        text=self.watermarkPanelTextButton.text()
        x=int(self.watermarkPanelXTextTextArea.text())
        y=int(self.watermarkPanelYTextTextArea.text())
        thickness=int(self.watermarkPanelTextThicknessTextArea.text())
        size=int(self.watermarkPanelTextSizeTextArea.text())
        self.watermarkText=text
        self.watermarkTextSize=size
        self.watermarkTextThickness=thickness
        self.watermarkTextCoordinates=x,y
        self.watermarkTextOpacity=int(self.watermarkPanelTextOpacitySliderValueLabel.text())
        self.worker.setTmApplication(self)
        self.worker.setOperation(25)
        self.worker.signal.connect(self.taskFinished)
        self.worker.start()
        self.showLoader()

    def validateWatermarkTextParameters(self):
        hasError=False
        text=self.watermarkPanelTextButton.text()
        x=self.watermarkPanelXTextTextArea.text()
        y=self.watermarkPanelYTextTextArea.text()
        thickness=self.watermarkPanelTextThicknessTextArea.text()
        size=self.watermarkPanelTextSizeTextArea.text()
        errorMessage=""
        errorMessageDialog=QtWidgets.QErrorMessage(self)
        if len(text)==0:
            errorMessage+="Invalid text input.\r\n"
            hasError=True
        if len(x)==0 or int(x)==0:
            errorMessage+="Invalid x-coordinte. \r\n"
            hasError=True
        if len(y)==0 or int(y)==0:
            errorMessage+="Invalid y-coordinte. \r\n"
            hasError=True
        if len(thickness)==0 or int(thickness)==0:
            errorMessage+="Invalid thickness. \r\n"
            hasError=True
        if len(size)==0 or int(size)==0:
            errorMessage+="Invalid text size. \r\n"
            hasError=True
        if hasError:
            errorMessageDialog.showMessage(errorMessage)
            errorMessageDialog.setWindowTitle("Error !")
            errorMessageDialog.show()
        else: self.applyTextWatermark()
        
    def createPanels(self):    
        self.lx1=1
        self.ly1=61
        self.lx2=828
        self.ly2=508
        self.rx1=self.lx1+1+self.lx2+219
        self.ry1=self.ly1
        self.rx2=199
        self.ry2=18


        #watermarkPanel

        self.watermarkPanelTitle=QLabel(self)
        self.watermarkPanelTitle.setGeometry(self.rx1,self.ry1+18+18+18+18+22+2,self.rx2,self.ry2+5)
        self.watermarkPanelTitle.setText("Watermark")
        self.watermarkPanelTitle.setAlignment(QtCore.Qt.AlignCenter) 
        self.watermarkPanelTitle.hide()

        self.watermarkPanelImageRadioButton=QRadioButton(self)
        self.watermarkPanelImageRadioButton.setGeometry(self.rx1+30,self.ry1+18+18+18+18+22+2+18+15,self.rx2,self.ry2+5)
        self.watermarkPanelImageRadioButton.setText("Image")
        self.watermarkPanelImageRadioButton.setChecked(True)
        self.watermarkPanelImageRadioButton.clicked.connect(self.showWatermarkImagePanel)
        self.watermarkPanelImageRadioButton.hide()

        self.watermarkPanelTextRadioButton=QRadioButton(self)
        self.watermarkPanelTextRadioButton.setGeometry(self.rx1+120,self.ry1+18+18+18+18+22+2+18+15,self.rx2,self.ry2+5)
        self.watermarkPanelTextRadioButton.setText("Text")
        self.watermarkPanelTextRadioButton.clicked.connect(self.showWatermarkTextPanel)
        self.watermarkPanelTextRadioButton.hide()

        #watermarkTextPanel

        self.watermarkPanelTextLabel=QLabel(self)
        self.watermarkPanelTextLabel.setGeometry(self.rx1+10,self.ry1+18+18+18+18+22+2+18+15+40,45,self.ry2)
        self.watermarkPanelTextLabel.setText("Text : ")
        self.watermarkPanelTextLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.watermarkPanelTextLabel.hide()
        
        self.watermarkPanelTextButton=QLineEdit("",self)
        self.watermarkPanelTextButton.setGeometry(self.rx1+60,self.ry1+18+18+18+18+22+2+18+15+40,85,self.ry2+5)
        self.watermarkPanelTextButton.hide()

        self.watermarkPanelXTextTitleLabel=QLabel(self)
        self.watermarkPanelXTextTitleLabel.setGeometry(self.rx1,self.ry1+18+18+18+18+22+2+18+15+40+30+10,45,self.ry2)
        self.watermarkPanelXTextTitleLabel.setText("X : ")
        self.watermarkPanelXTextTitleLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.watermarkPanelXTextTitleLabel.hide()

        self.watermarkPanelXTextTextArea=QLineEdit("0",self)
        self.watermarkPanelXTextTextArea.setGeometry(self.rx1+35,self.ry1+18+18+18+18+22+2+18+15+40+30+10,40,self.ry2)
        self.watermarkPanelXTextTextArea.hide()

        self.watermarkPanelYTextTitleLabel=QLabel(self)
        self.watermarkPanelYTextTitleLabel.setGeometry(self.rx1+35+35+10,self.ry1+18+18+18+18+22+2+18+15+40+30+10,45,self.ry2)
        self.watermarkPanelYTextTitleLabel.setText("Y : ")
        self.watermarkPanelYTextTitleLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.watermarkPanelYTextTitleLabel.hide()

        self.watermarkPanelYTextTextArea=QLineEdit("0",self)
        self.watermarkPanelYTextTextArea.setGeometry(self.rx1+35+35+35+10,self.ry1+18+18+18+18+22+2+18+15+40+30+10,40,self.ry2)
        self.watermarkPanelYTextTextArea.hide()

        self.watermarkPanelTextThicknessLabel=QLabel(self)
        self.watermarkPanelTextThicknessLabel.setGeometry(self.rx1+10,self.ry1+18+18+18+18+22+2+18+15+40+30+10+35,60,self.ry2)
        self.watermarkPanelTextThicknessLabel.setText("Thickness : ")
        self.watermarkPanelTextThicknessLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.watermarkPanelTextThicknessLabel.hide()
        
        self.watermarkPanelTextThicknessTextArea=QLineEdit("0",self)
        self.watermarkPanelTextThicknessTextArea.setGeometry(self.rx1+15+55,self.ry1+18+18+18+18+22+2+18+15+40+30+10+35,40,self.ry2)
        self.watermarkPanelTextThicknessTextArea.hide()

        self.watermarkPanelTextSizeLabel=QLabel(self)
        self.watermarkPanelTextSizeLabel.setGeometry(self.rx1+15+55+40+5,self.ry1+18+18+18+18+22+2+18+15+40+30+10+35,40,self.ry2)
        self.watermarkPanelTextSizeLabel.setText("Size : ")
        self.watermarkPanelTextSizeLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.watermarkPanelTextSizeLabel.hide()

        self.watermarkPanelTextSizeTextArea=QLineEdit("0",self)
        self.watermarkPanelTextSizeTextArea.setGeometry(self.rx1+15+55+40+10+35,self.ry1+18+18+18+18+22+2+18+15+40+30+10+35,40,self.ry2)
        self.watermarkPanelTextSizeTextArea.hide()

        self.watermarkPanelTextOpacityPanel=QLabel("Opacity : ",self)
        self.watermarkPanelTextOpacityPanel.setGeometry(self.rx1+10,self.ry1+18+18+18+18+22+2+18+15+40+30+30+45,50,self.ry2)
        self.watermarkPanelTextOpacityPanel.setAlignment(QtCore.Qt.AlignCenter) 
        self.watermarkPanelTextOpacityPanel.hide()

        self.watermarkPanelTextOpacitySlider=QSlider(Qt.Horizontal,self)
        self.watermarkPanelTextOpacitySlider.setFocusPolicy(Qt.NoFocus)
        self.watermarkPanelTextOpacitySlider.setTickPosition(QSlider.NoTicks)
        self.watermarkPanelTextOpacitySlider.setTickInterval(10)
        self.watermarkPanelTextOpacitySlider.setSingleStep(1)
        self.watermarkPanelTextOpacitySlider.setValue(50)
        self.watermarkPanelTextOpacitySlider.setGeometry(self.rx1+10+55,self.ry1+18+18+18+18+22+2+18+15+40+30+60+15,100,20)
        self.watermarkPanelTextOpacitySlider.valueChanged.connect(lambda: self.setOpacitySliderValue(2))
        self.watermarkPanelTextOpacitySlider.hide()

        self.watermarkPanelTextOpacitySliderValueLabel=QLabel(self)
        self.watermarkPanelTextOpacitySliderValueLabel.setGeometry(self.rx1+10+145,self.ry1+18+18+18+18+22+2+18+15+40+30+30+45,50,self.ry2)
        self.watermarkPanelTextOpacitySliderValueLabel.setText("50")
        self.watermarkPanelTextOpacitySliderValueLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.watermarkPanelTextOpacitySliderValueLabel.hide()

        self.watermarkPanelTextOKButton=QPushButton("OK",self)
        self.watermarkPanelTextOKButton.setGeometry(self.rx1+10+15,self.ry1+18+18+18+18+22+2+18+15+40+30+30+20+60,70,self.ry2+5)
        self.watermarkPanelTextOKButton.setIcon(QIcon("img/ok.png"))
        self.watermarkPanelTextOKButton.clicked.connect(self.validateWatermarkTextParameters)
        self.watermarkPanelTextOKButton.hide()

        self.watermarkPanelTextCloseButton=QPushButton("Close",self)
        self.watermarkPanelTextCloseButton.setGeometry(self.rx1+10+92,self.ry1+18+18+18+18+22+2+18+15+40+30+30+20+60,70,self.ry2+5)
        self.watermarkPanelTextCloseButton.setIcon(QIcon("img/cancel.png"))
        self.watermarkPanelTextCloseButton.clicked.connect(self.hideWatermarkPanel)
        self.watermarkPanelTextCloseButton.hide()

        #watermarkImagePanel

        self.watermarkPanelImageLabel=QLabel(self)
        self.watermarkPanelImageLabel.setGeometry(self.rx1+10,self.ry1+18+18+18+18+22+2+18+15+40,45,self.ry2)
        self.watermarkPanelImageLabel.setText("Image : ")
        self.watermarkPanelImageLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.watermarkPanelImageLabel.hide()
        
        self.watermarkPanelImageButton=QPushButton("Choose...",self)
        self.watermarkPanelImageButton.setGeometry(self.rx1+60,self.ry1+18+18+18+18+22+2+18+15+40,85,self.ry2+5)
        self.watermarkPanelImageButton.setIcon(QIcon("img/choose.png"))
        self.watermarkPanelImageButton.clicked.connect(self.openWatermarkImageChooser)
        self.watermarkPanelImageButton.hide()

        self.watermarkPanelXImageTitleLabel=QLabel(self)
        self.watermarkPanelXImageTitleLabel.setGeometry(self.rx1,self.ry1+18+18+18+18+22+2+18+15+40+30+10,45,self.ry2)
        self.watermarkPanelXImageTitleLabel.setText("X : ")
        self.watermarkPanelXImageTitleLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.watermarkPanelXImageTitleLabel.hide()

        self.watermarkPanelXImageTextArea=QLineEdit("0",self)
        self.watermarkPanelXImageTextArea.setGeometry(self.rx1+35,self.ry1+18+18+18+18+22+2+18+15+40+30+10,40,self.ry2)
        self.watermarkPanelXImageTextArea.hide()

        self.watermarkPanelYImageTitleLabel=QLabel(self)
        self.watermarkPanelYImageTitleLabel.setGeometry(self.rx1+35+35+10,self.ry1+18+18+18+18+22+2+18+15+40+30+10,45,self.ry2)
        self.watermarkPanelYImageTitleLabel.setText("Y : ")
        self.watermarkPanelYImageTitleLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.watermarkPanelYImageTitleLabel.hide()

        self.watermarkPanelYImageTextArea=QLineEdit("0",self)
        self.watermarkPanelYImageTextArea.setGeometry(self.rx1+35+35+35+10,self.ry1+18+18+18+18+22+2+18+15+40+30+10,40,self.ry2)
        self.watermarkPanelYImageTextArea.hide()

        self.watermarkPanelImageOpacityPanel=QLabel(self)
        self.watermarkPanelImageOpacityPanel.setGeometry(self.rx1+10,self.ry1+18+18+18+18+22+2+18+15+40+30+30+20,50,self.ry2)
        self.watermarkPanelImageOpacityPanel.setText("Opacity : ")
        self.watermarkPanelImageOpacityPanel.setAlignment(QtCore.Qt.AlignCenter) 
        self.watermarkPanelImageOpacityPanel.hide()

        self.watermarkPanelImageOpacitySlider=QSlider(Qt.Horizontal,self)
        self.watermarkPanelImageOpacitySlider.setFocusPolicy(Qt.NoFocus)
        self.watermarkPanelImageOpacitySlider.setTickPosition(QSlider.NoTicks)
        self.watermarkPanelImageOpacitySlider.setTickInterval(10)
        self.watermarkPanelImageOpacitySlider.setSingleStep(1)
        self.watermarkPanelImageOpacitySlider.setValue(50)
        self.watermarkPanelImageOpacitySlider.setGeometry(self.rx1+10+55,self.ry1+18+18+18+18+22+2+18+15+40+30+50,100,20)
        self.watermarkPanelImageOpacitySlider.valueChanged.connect(lambda: self.setOpacitySliderValue(1))
        self.watermarkPanelImageOpacitySlider.hide()

        self.watermarkPanelImageOpacitySliderValueLabel=QLabel(self)
        self.watermarkPanelImageOpacitySliderValueLabel.setGeometry(self.rx1+10+145,self.ry1+18+18+18+18+22+2+18+15+40+30+30+20,50,self.ry2)
        self.watermarkPanelImageOpacitySliderValueLabel.setText("50")
        self.watermarkPanelImageOpacitySliderValueLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.watermarkPanelImageOpacitySliderValueLabel.hide()

        self.watermarkPanelImageOKButton=QPushButton("OK",self)
        self.watermarkPanelImageOKButton.setGeometry(self.rx1+10+15,self.ry1+18+18+18+18+22+2+18+15+40+30+30+20+40,70,self.ry2+5)
        self.watermarkPanelImageOKButton.setIcon(QIcon("img/ok.png"))
        self.watermarkPanelImageOKButton.clicked.connect(self.validateWatermarkImageParameters)
        self.watermarkPanelImageOKButton.hide()

        self.watermarkPanelImageCloseButton=QPushButton("Close",self)
        self.watermarkPanelImageCloseButton.setGeometry(self.rx1+10+92,self.ry1+18+18+18+18+22+2+18+15+40+30+30+20+40,70,self.ry2+5)
        self.watermarkPanelImageCloseButton.setIcon(QIcon("img/cancel.png"))
        self.watermarkPanelImageCloseButton.clicked.connect(self.hideWatermarkPanel)
        self.watermarkPanelImageCloseButton.hide()


        #textAddingPanel

        self.textPanelTitle=QLabel(self)
        self.textPanelTitle.setGeometry(self.rx1,self.ry1+18+18+18+18+22+2,self.rx2,self.ry2+5)
        self.textPanelTitle.setText("Add Text")
        self.textPanelTitle.setAlignment(QtCore.Qt.AlignCenter) 
        self.textPanelTitle.hide()

        self.textPanelTextLabel=QLabel(self)
        self.textPanelTextLabel.setGeometry(self.rx1+10,self.ry1+18+18+18+18+22+2+18+15,self.rx2,self.ry2+5)
        self.textPanelTextLabel.setText("Text : ")
        self.textPanelTextLabel.setAlignment(QtCore.Qt.AlignLeft) 
        self.textPanelTextLabel.hide()

        self.textPanelTextArea=QLineEdit("",self)
        self.textPanelTextArea.setGeometry(self.rx1+5+40,self.ry1+18+18+18+18+22+2+18+12,145,self.ry2)
        self.textPanelTextArea.textChanged.connect(self.updateTextPanelParameters)
        self.textPanelTextArea.hide()

        self.textPanelFontLabel=QLabel(self)
        self.textPanelFontLabel.setGeometry(self.rx1+10,self.ry1+18+18+18+18+22+2+18+15+30,self.rx2,self.ry2+5)
        self.textPanelFontLabel.setText("Font : ")
        self.textPanelFontLabel.setAlignment(QtCore.Qt.AlignLeft) 
        self.textPanelFontLabel.hide()

        self.textPanelFontButton=QPushButton("Select",self)
        self.textPanelFontButton.setGeometry(self.rx1+10+35,self.ry1+18+18+18+18+22+2+18+15+25,110,self.ry2+5)
        self.textPanelFontButton.setIcon(QIcon("img/choose.png"))
        self.textPanelFontButton.clicked.connect(self.showFontSelectorDialog)
        self.textPanelFontButton.hide()

        self.textPanelFontSizeLabel=QLabel(self)
        self.textPanelFontSizeLabel.setGeometry(self.rx1+10+35+117,self.ry1+18+18+18+18+22+2+18+15+26,30,self.ry2+2)
        self.textPanelFontSizeLabel.setText("0")
        self.textPanelFontSizeLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.textPanelFontSizeLabel.setStyleSheet("background-color:white")
        self.textPanelFontSizeLabel.hide()

        self.textPanelColorLabel=QLabel(self)
        self.textPanelColorLabel.setGeometry(self.rx1+10,self.ry1+18+18+18+18+22+2+18+15+60,self.rx2,self.ry2+5)
        self.textPanelColorLabel.setText("Color : ")
        self.textPanelColorLabel.setAlignment(QtCore.Qt.AlignLeft) 
        self.textPanelColorLabel.hide()

        self.textPanelColorButton=QPushButton("Pick",self)
        self.textPanelColorButton.setGeometry(self.rx1+10+35,self.ry1+18+18+18+18+22+2+18+15+25+15+15,100,self.ry2+5)
        self.textPanelColorButton.setIcon(QIcon("img/pick.png"))
        self.textPanelColorButton.clicked.connect(self.showColorSelectorDialog)
        self.textPanelColorButton.hide()

        self.textPanelTextCoordinatesLabel=QLabel(self)
        self.textPanelTextCoordinatesLabel.setGeometry(self.rx1+10,self.ry1+18+18+18+18+22+2+18+15+25+15+50,self.rx2,self.ry2+5)
        self.textPanelTextCoordinatesLabel.setText("(X,Y) : ")
        self.textPanelTextCoordinatesLabel.setAlignment(QtCore.Qt.AlignLeft) 
        self.textPanelTextCoordinatesLabel.hide()

        self.textPanelXCoordinate=QLineEdit("",self)
        self.textPanelXCoordinate.setGeometry(self.rx1+10+35,self.ry1+18+18+18+18+22+2+18+15+25+15+48,50,self.ry2)
        self.textPanelXCoordinate.textChanged.connect(self.updateTextPanelParameters)
        self.textPanelXCoordinate.hide()

        self.textPanelYCoordinate=QLineEdit("",self)
        self.textPanelYCoordinate.setGeometry(self.rx1+10+35+55,self.ry1+18+18+18+18+22+2+18+15+25+15+48,50,self.ry2)
        self.textPanelYCoordinate.textChanged.connect(self.updateTextPanelParameters)
        self.textPanelYCoordinate.hide()

        self.textPanelOKButton=QPushButton("OK",self)
        self.textPanelOKButton.setGeometry(self.rx1+10+15,self.ry1+18+18+18+18+22+2+18+15+25+15+85,70,self.ry2+5)
        self.textPanelOKButton.setIcon(QIcon("img/ok.png"))
        self.textPanelOKButton.clicked.connect(self.applyText)
        self.textPanelOKButton.hide()

        self.textPanelCancelButton=QPushButton("Close",self)
        self.textPanelCancelButton.setGeometry(self.rx1+10+92,self.ry1+18+18+18+18+22+2+18+15+25+15+85,70,self.ry2+5)
        self.textPanelCancelButton.setIcon(QIcon("img/cancel.png"))
        self.textPanelCancelButton.clicked.connect(self.hideTextPanel)
        self.textPanelCancelButton.hide()

        #cropPanel

        self.cropPanelTitle=QLabel(self)
        self.cropPanelTitle.setGeometry(self.rx1,self.ry1+18+18+18+18+22+2,self.rx2,self.ry2+5)
        self.cropPanelTitle.setText("Crop Image")
        self.cropPanelTitle.setAlignment(QtCore.Qt.AlignCenter) 
        self.cropPanelTitle.hide()

        self.cropPanelXLabel=QLabel(self)
        self.cropPanelXLabel.setGeometry(self.rx1,self.ry1+18+18+18+18+24+18+15,25,self.ry2)
        self.cropPanelXLabel.setText("X:")
        self.cropPanelXLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.cropPanelXLabel.hide()

        self.cropPanelXTextArea=QLineEdit("0",self)
        self.cropPanelXTextArea.setGeometry(self.rx1+45,self.ry1+18+18+18+18+24+18+15,50,self.ry2)
        self.cropPanelXTextArea.textChanged.connect(self.updateCropParameters)
        self.cropPanelXTextArea.hide()

        self.cropPanelYLabel=QLabel(self)
        self.cropPanelYLabel.setGeometry(self.rx1+26+50+23,self.ry1+18+18+18+18+24+18+15,25,self.ry2)
        self.cropPanelYLabel.setText("Y:")
        self.cropPanelYLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.cropPanelYLabel.hide()

        self.cropPanelYTextArea=QLineEdit("0",self)
        self.cropPanelYTextArea.setGeometry(self.rx1+26+50+25+45,self.ry1+18+18+18+18+24+18+15,50,self.ry2)
        self.cropPanelYTextArea.textChanged.connect(self.updateCropParameters)
        self.cropPanelYTextArea.hide()

        self.cropPanelHeightLabel=QLabel(self)
        self.cropPanelHeightLabel.setGeometry(self.rx1,self.ry1+18+18+18+18+24+18+20+20,45,self.ry2)
        self.cropPanelHeightLabel.setText("Height:")
        self.cropPanelHeightLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.cropPanelHeightLabel.hide()

        self.cropPanelHeightTextArea=QLineEdit("0",self)
        self.cropPanelHeightTextArea.setGeometry(self.rx1+45,self.ry1+18+18+18+18+24+18+20+20,50,self.ry2)
        self.cropPanelHeightTextArea.textChanged.connect(self.updateCropParameters)
        self.cropPanelHeightTextArea.hide()

        self.cropPanelWidthLabel=QLabel(self)
        self.cropPanelWidthLabel.setGeometry(self.rx1+48+53,self.ry1+18+18+18+18+24+18+20+20,45,self.ry2)
        self.cropPanelWidthLabel.setText("Width:")
        self.cropPanelWidthLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.cropPanelWidthLabel.hide()

        self.cropPanelWidthTextArea=QLineEdit("0",self)
        self.cropPanelWidthTextArea.setGeometry(self.rx1+48+53+45,self.ry1+18+18+18+18+24+18+20+20,50,self.ry2)
        self.cropPanelWidthTextArea.textChanged.connect(self.updateCropParameters)
        self.cropPanelWidthTextArea.hide()

        self.cropPanelPreviewButton=QPushButton("Preview",self)
        self.cropPanelPreviewButton.setGeometry(self.rx1+20+15,self.ry1+18+18+18+18+24+18+20+20+20+5,65,self.ry2+10)
        self.cropPanelPreviewButton.setIcon(QIcon("img/previewButton.png"))
        self.cropPanelPreviewButton.clicked.connect(self.getPreviewForCrop)
        self.cropPanelPreviewButton.hide()

        self.cropPanelCropButton=QPushButton("Crop",self)
        self.cropPanelCropButton.setGeometry(self.rx1+20+50+10+25,self.ry1+18+18+18+18+24+18+20+20+20+5,50,self.ry2+10)
        self.cropPanelCropButton.setIcon(QIcon("img/cropButton.png"))
        self.cropPanelCropButton.clicked.connect(self.performCrop)
        self.cropPanelCropButton.hide()


        #flipPanel

        self.flipPanelTitle=QLabel(self)
        self.flipPanelTitle.setGeometry(self.rx1,self.ry1+18+18+18+18+22+2,self.rx2,self.ry2+5)
        self.flipPanelTitle.setText("Flip Image")
        self.flipPanelTitle.setAlignment(QtCore.Qt.AlignCenter) 
        self.flipPanelTitle.hide()

        self.flipPanelHorizontalRadioButton=QRadioButton(self)
        self.flipPanelHorizontalRadioButton.setGeometry(self.rx1+20,self.ry1+18+18+18+18+24+18+15,80,self.ry2)
        self.flipPanelHorizontalRadioButton.setText("Horizontal")
        self.flipPanelHorizontalRadioButton.hide()

        self.flipPanelVerticalRadioButton=QRadioButton(self)
        self.flipPanelVerticalRadioButton.setGeometry(self.rx1+120,self.ry1+18+18+18+18+24+18+15,80,self.ry2)
        self.flipPanelVerticalRadioButton.setText("Vertical")
        self.flipPanelVerticalRadioButton.hide()

        self.flipPanelOKButton=QPushButton("OK",self)
        self.flipPanelOKButton.setGeometry(self.rx1+20+10,self.ry1+18+18+18+18+24+18+20+23,70,self.ry2+10)
        self.flipPanelOKButton.setIcon(QIcon("img/ok.png"))
        self.flipPanelOKButton.clicked.connect(self.performFlip)
        self.flipPanelOKButton.hide()
        
        self.flipPanelCancelButton=QPushButton("Close",self)
        self.flipPanelCancelButton.setGeometry(self.rx1+20+15+70,self.ry1+18+18+18+18+24+18+20+23,70,self.ry2+10)
        self.flipPanelCancelButton.setIcon(QIcon("img/cancel.png"))
        self.flipPanelCancelButton.clicked.connect(self.hideFlipPanel)
        self.flipPanelCancelButton.hide()

        #rotatePanel

        self.rotatePanelTitle=QLabel(self)
        self.rotatePanelTitle.setGeometry(self.rx1,self.ry1+18+18+18+18+22+2,self.rx2,self.ry2+5)
        self.rotatePanelTitle.setText("Rotate Image")
        self.rotatePanelTitle.setAlignment(QtCore.Qt.AlignCenter) 
        self.rotatePanelTitle.hide()
        
        self.rotatePanelClockwiseRadioButton=QRadioButton(self)
        self.rotatePanelClockwiseRadioButton.setGeometry(self.rx1+5,self.ry1+18+18+18+18+24+18+15,110,self.ry2)
        self.rotatePanelClockwiseRadioButton.setText("Clockwise - 90°")
        self.rotatePanelClockwiseRadioButton.hide()

        self.rotatePanelAntiClockwiseRadioButton=QRadioButton(self)
        self.rotatePanelAntiClockwiseRadioButton.setGeometry(self.rx1+5,self.ry1+18+18+18+18+24+18+15+30,110,self.ry2)
        self.rotatePanelAntiClockwiseRadioButton.setText("Anticlockwise - 90°")
        self.rotatePanelAntiClockwiseRadioButton.hide()
        
        self.rotatePanelOneEightyDegreeRadioButton=QRadioButton(self)
        self.rotatePanelOneEightyDegreeRadioButton.setGeometry(self.rx1+5,self.ry1+18+18+18+18+24+18+15+30+30,110,self.ry2)
        self.rotatePanelOneEightyDegreeRadioButton.setText("180°")
        self.rotatePanelOneEightyDegreeRadioButton.hide()

        self.rotatePanelOKButton=QPushButton("OK",self)
        self.rotatePanelOKButton.setGeometry(self.rx1+20+10,self.ry1+18+18+18+18+24+18+15+30+30+23+5,70,self.ry2+10)
        self.rotatePanelOKButton.setIcon(QIcon("img/ok.png"))
        self.rotatePanelOKButton.clicked.connect(self.performRotation)
        self.rotatePanelOKButton.hide()
        
        self.rotatePanelCancelButton=QPushButton("Close",self)
        self.rotatePanelCancelButton.setGeometry(self.rx1+20+15+70,self.ry1+18+18+18+18+24+18+15+30+30+23+5,70,self.ry2+10)
        self.rotatePanelCancelButton.setIcon(QIcon("img/cancel.png"))
        self.rotatePanelCancelButton.clicked.connect(self.hideRotatePanel)
        self.rotatePanelCancelButton.hide()

        #overlayPanel

        self.overlayPanelTitle=QLabel(self)
        self.overlayPanelTitle.setGeometry(self.rx1,self.ry1+18+18+18+18+22+2,self.rx2,self.ry2+5)
        self.overlayPanelTitle.setText("Overlay")
        self.overlayPanelTitle.setAlignment(QtCore.Qt.AlignCenter) 
        self.overlayPanelTitle.hide()


        self.overlayPanelImageTitle=QLabel(self)
        self.overlayPanelImageTitle.setGeometry(self.rx1+10,self.ry1+18+18+18+18+24+18+10,45,self.ry2)
        self.overlayPanelImageTitle.setText("Image : ")
        self.overlayPanelImageTitle.setAlignment(QtCore.Qt.AlignCenter) 
        self.overlayPanelImageTitle.hide()

        
        self.overlayPanelImageButton=QPushButton("Choose...",self)
        self.overlayPanelImageButton.setGeometry(self.rx1+10+45,self.ry1+18+18+18+18+24+18+10,95,self.ry2+5)
        self.overlayPanelImageButton.setIcon(QIcon("img/choose.png"))
        self.overlayPanelImageButton.clicked.connect(self.openOverlayImageChooser)
        self.overlayPanelImageButton.hide()

        self.overlayPanelImageLabel=QLabel(self)
        self.overlayPanelImageLabel.setGeometry(self.rx1+10+30,self.ry1+18+18+18+18+24+18+8,110,self.ry2+5)
        self.overlayPanelImageLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.overlayPanelImageLabel.hide()

        self.overlayPanelXLabel=QLabel(self)
        self.overlayPanelXLabel.setGeometry(self.rx1,self.ry1+18+18+18+18+24+18+20+20,45,self.ry2)
        self.overlayPanelXLabel.setText("X:")
        self.overlayPanelXLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.overlayPanelXLabel.hide()

        self.overlayPanelXTextArea=QLineEdit("0",self)
        self.overlayPanelXTextArea.setGeometry(self.rx1+45,self.ry1+18+18+18+18+24+18+20+20,50,self.ry2)
        self.overlayPanelXTextArea.textChanged.connect(self.updateOverlayParameters)
        self.overlayPanelXTextArea.hide()

        self.overlayPanelYLabel=QLabel(self)
        self.overlayPanelYLabel.setGeometry(self.rx1+48+53,self.ry1+18+18+18+18+24+18+20+20,45,self.ry2)
        self.overlayPanelYLabel.setText("Y:")
        self.overlayPanelYLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.overlayPanelYLabel.hide()

        self.overlayPanelYTextArea=QLineEdit("0",self)
        self.overlayPanelYTextArea.setGeometry(self.rx1+48+53+45,self.ry1+18+18+18+18+24+18+20+20,50,self.ry2)
        self.overlayPanelYTextArea.textChanged.connect(self.updateOverlayParameters)
        self.overlayPanelYTextArea.hide()

        self.overlayPanelOKButton=QPushButton("OK",self)
        self.overlayPanelOKButton.setGeometry(self.rx1+20+10,self.ry1+18+18+18+18+24+18+20+20+20+10,70,self.ry2+10)
        self.overlayPanelOKButton.setIcon(QIcon("img/ok.png"))
        self.overlayPanelOKButton.clicked.connect(self.performOverlay)
        self.overlayPanelOKButton.hide()
        
        self.overlayPanelCancelButton=QPushButton("Close",self)
        self.overlayPanelCancelButton.setGeometry(self.rx1+20+15+70,self.ry1+18+18+18+18+24+18+20+20+20+10,70,self.ry2+10)
        self.overlayPanelCancelButton.setIcon(QIcon("img/cancel.png"))
        self.overlayPanelCancelButton.clicked.connect(self.hideOverlayPanel)
        self.overlayPanelCancelButton.hide()

    def updateBars(self):
        self.toolbar.setEnabled(True)
        self.saveAct.setEnabled(True)
        self.brightnessAct.setEnabled(True)
        self.contrastAct.setEnabled(True)
        self.resizeAct.setEnabled(True)
        self.zoomInAct.setEnabled(True)
        self.zoomOutAct.setEnabled(True)
        self.blurMenu.setEnabled(True)
        self.borderAct.setEnabled(True)

    def update(self):
        self.updateImageOnUI()
        self.updateBars()

    def showSliderValue(self):
        print(self.slider.value())

    def createStatusBar(self):
        self.statusBar=QStatusBar()
        self.statusBar.setStyleSheet("background:#FFFCE3")
        self.statusBar.setFixedHeight(30)
        self.setStatusBar(self.statusBar)
        self.images["status"]="Select an Image..."
        self.updateStatusBar()
    
    def updateResizeParameters(self):
        try:
            self.destHeight=int(self.resizeHeightTextArea.text())
            self.destWidth=int(self.resizeWidthTextArea.text())
        except:
            self.destHeight=0
            self.destWidth=0

    def updateOverlayParameters(self):
        self.startingOverlayX=self.overlayPanelXTextArea.text()
        self.startingOverlayY=self.overlayPanelYTextArea.text()
    
    def updateCropParameters(self):
        self.startingPreviewX=self.cropPanelXTextArea.text()
        self.startingPreviewY=self.cropPanelYTextArea.text()
        self.endingPreviewX=self.cropPanelHeightTextArea.text()
        self.endingPreviewY=self.cropPanelWidthTextArea.text()
    
    def getPreviewForCrop(self):
        self.worker.setTmApplication(self)
        self.worker.setOperation(4)
        self.worker.signal.connect(self.taskFinished)
        self.worker.start()
        self.showLoader()
    
    def performOverlay(self):
        self.worker.setTmApplication(self)
        self.worker.setOperation(11)
        self.worker.signal.connect(self.taskFinished)
        self.worker.start()
        self.showLoader()
    
    def performFlip(self):
        if self.flipPanelHorizontalRadioButton.isChecked():
            self.worker.setTmApplication(self)
            self.worker.setOperation(6)
            self.worker.signal.connect(self.taskFinished)
            self.worker.start()
            self.showLoader()
            self.hideCropPanel()
        elif self.flipPanelVerticalRadioButton.isChecked():
            self.worker.setTmApplication(self)
            self.worker.setOperation(7)
            self.worker.signal.connect(self.taskFinished)
            self.worker.start()
            self.showLoader()
            self.hideCropPanel()
    
    def performCrop(self):
        self.worker.setTmApplication(self)
        self.worker.setOperation(5)
        self.worker.signal.connect(self.taskFinished)
        self.worker.start()
        self.showLoader()
        self.hideCropPanel()

    def performRotation(self):
        if self.rotatePanelClockwiseRadioButton.isChecked():
            self.worker.setTmApplication(self)
            self.worker.setOperation(8)
            self.worker.signal.connect(self.taskFinished)
            self.worker.start()
            self.showLoader()
            self.hideCropPanel()
        elif self.rotatePanelAntiClockwiseRadioButton.isChecked():
            self.worker.setTmApplication(self)
            self.worker.setOperation(9)
            self.worker.signal.connect(self.taskFinished)
            self.worker.start()
            self.showLoader()
            self.hideCropPanel()
        elif self.rotatePanelOneEightyDegreeRadioButton.isChecked():
            self.worker.setTmApplication(self)
            self.worker.setOperation(10)
            self.worker.signal.connect(self.taskFinished)
            self.worker.start()
            self.showLoader()
            self.hideCropPanel()

    def hideRotatePanel(self):
        self.rotatePanelTitle.hide()
        self.rotatePanelClockwiseRadioButton.hide()
        self.rotatePanelAntiClockwiseRadioButton.hide()
        self.rotatePanelOneEightyDegreeRadioButton.hide()
        self.rotatePanelOKButton.hide()
        self.rotatePanelCancelButton.hide()
    
    def hideFlipPanel(self):
        self.flipPanelTitle.hide()
        self.flipPanelHorizontalRadioButton.hide()
        self.flipPanelVerticalRadioButton.hide()
        self.flipPanelOKButton.hide()
        self.flipPanelCancelButton.hide()
    
    def hideOverlayPanel(self):
        self.overlayPanelTitle.hide()
        self.overlayPanelImageTitle.hide()
        self.overlayPanelImageButton.hide()
        self.overlayPanelXLabel.hide()
        self.overlayPanelXTextArea.hide()
        self.overlayPanelYLabel.hide()
        self.overlayPanelYTextArea.hide()
        self.overlayPanelOKButton.hide()
        self.overlayPanelCancelButton.hide()
        self.overlayPanelImageLabel.hide()
    
    def showTextPanel(self):
        self.hideCropPanel()
        self.hideOverlayPanel()
        self.hideFlipPanel()
        self.hideRotatePanel()
        self.textPanelTitle.show()
        self.textPanelTextLabel.show()
        self.textPanelTextArea.show()
        self.textPanelFontLabel.show()
        self.textPanelFontButton.show()
        self.textPanelFontSizeLabel.show()
        self.textPanelColorLabel.show()
        self.textPanelColorButton.show()
        self.textPanelTextCoordinatesLabel.show()
        self.textPanelXCoordinate.show()
        self.textPanelYCoordinate.show()
        self.textPanelOKButton.show()
        self.textPanelCancelButton.show()
    
    def hideTextPanel(self):
        self.textPanelTitle.hide()
        self.textPanelTextLabel.hide()
        self.textPanelTextArea.hide()
        self.textPanelFontLabel.hide()
        self.textPanelFontButton.hide()
        self.textPanelFontSizeLabel.hide()
        self.textPanelColorLabel.hide()
        self.textPanelColorButton.hide()
        self.textPanelTextCoordinatesLabel.hide()
        self.textPanelXCoordinate.hide()
        self.textPanelYCoordinate.hide()
        self.textPanelOKButton.hide()
        self.textPanelCancelButton.hide()
    
    def showOverlayPanel(self):
        self.hideCropPanel()
        self.hideTextPanel()
        self.hideFlipPanel()
        self.hideRotatePanel()
        self.overlayPanelTitle.show()
        self.overlayPanelImageTitle.show()
        self.overlayPanelImageButton.show()
        self.overlayPanelXLabel.show()
        self.overlayPanelXTextArea.show()
        self.overlayPanelYLabel.show()
        self.overlayPanelYTextArea.show()
        self.overlayPanelOKButton.show()
        self.overlayPanelCancelButton.show()
    
    def showFlipPanel(self):
        self.hideCropPanel()
        self.hideOverlayPanel()
        self.hideTextPanel()
        self.hideRotatePanel()
        self.flipPanelTitle.show()
        self.flipPanelHorizontalRadioButton.show()
        self.flipPanelVerticalRadioButton.show()
        self.flipPanelOKButton.show()
        self.flipPanelCancelButton.show()
    
    def showRotatePanel(self):
        self.hideCropPanel()
        self.hideOverlayPanel()
        self.hideFlipPanel()
        self.hideTextPanel()
        self.rotatePanelTitle.show()
        self.rotatePanelClockwiseRadioButton.show()
        self.rotatePanelAntiClockwiseRadioButton.show()
        self.rotatePanelOneEightyDegreeRadioButton.show()
        self.rotatePanelOKButton.show()
        self.rotatePanelCancelButton.show()

    def showCropPanel(self):
        self.hideTextPanel()
        self.hideOverlayPanel()
        self.hideFlipPanel()
        self.hideRotatePanel()
        self.cropPanelTitle.show()
        self.cropPanelXLabel.show()
        self.cropPanelXTextArea.show()
        self.cropPanelYLabel.show()
        self.cropPanelYTextArea.show()
        self.cropPanelHeightLabel.show()
        self.cropPanelHeightTextArea.show()
        self.cropPanelWidthLabel.show()
        self.cropPanelWidthTextArea.show()
        self.cropPanelPreviewButton.show()
        self.cropPanelCropButton.show()
    
    def hideCropPanel(self):
        self.cropPanelTitle.hide()
        self.cropPanelXLabel.hide()
        self.cropPanelXTextArea.hide()
        self.cropPanelYLabel.hide()
        self.cropPanelYTextArea.hide()
        self.cropPanelHeightLabel.hide()
        self.cropPanelHeightTextArea.hide()
        self.cropPanelWidthLabel.hide()
        self.cropPanelWidthTextArea.hide()
        self.cropPanelPreviewButton.hide()
        self.cropPanelCropButton.hide()

    def performGrayScale(self):
        self.worker.setTmApplication(self)
        self.worker.setOperation(1)
        self.worker.signal.connect(self.taskFinished)
        self.worker.start()
        self.showLoader()
    
    def showLoader(self):
        self.loader=QMovie("img/loader.gif")
        self.loaderLabel=QLabel(self)
        self.loaderLabel.setGeometry(590,220,120,120)
        #self.loaderLabel.setStyleSheet("border:2px solid black")
        self.loaderLabel.setMovie(self.loader)
        self.loader.start()
        self.loaderLabel.show()
    
    def hideLoader(self):
        self.loaderLabel.setVisible(False)
        self.update()
    
    def taskFinished(self,result):
        self.updateStatusBar()
        self.hideLoader()

    def createToolBar(self):
        grayScaleAct = QAction(QtGui.QIcon('img/gs.png'), 'Gray Scale', self)
        grayScaleAct.setStatusTip('Gray Scale')
        grayScaleAct.triggered.connect(self.performGrayScale)

        flipAct = QAction(QtGui.QIcon('img/flip.png'), 'Flip', self)
        flipAct.setStatusTip('Flip')
        flipAct.triggered.connect(self.showFlipPanel)

        separator1 = QAction(QtGui.QIcon('img/rotation.png'), 'Separator', self)
        separator1.setSeparator(True)

        rotationAct = QAction(QtGui.QIcon('img/rotation.png'), 'Rotation', self)
        rotationAct.setStatusTip('Rotation')
        rotationAct.triggered.connect(self.showRotatePanel)

        cropAct = QAction(QtGui.QIcon('img/crop.png'), 'Crop', self)
        cropAct.setStatusTip('Crop')
        cropAct.triggered.connect(self.showCropPanel)

        overlayAct = QAction(QtGui.QIcon('img/overlay.png'), 'Overlay', self)
        overlayAct.setStatusTip('Overlay')
        overlayAct.triggered.connect(self.showOverlayPanel)

        separator2 = QAction(QtGui.QIcon('img/rotation.png'), 'Separator', self)
        separator2.setSeparator(True)

        invertAct = QAction(QtGui.QIcon('img/invert.png'), 'Invert', self)
        invertAct.setStatusTip('Invert')
        invertAct.triggered.connect(self.applyInvert)

        textAct = QAction(QtGui.QIcon('img/text.png'), 'Text', self)
        textAct.setStatusTip('Text')
        textAct.triggered.connect(self.showTextPanel)
        
        separator3 = QAction(QtGui.QIcon('img/rotation.png'), 'Separator', self)
        separator3.setSeparator(True)

        sharpAct = QAction(QtGui.QIcon('img/sharp.png'), 'Sharp', self)
        sharpAct.setStatusTip('Sharp')
        sharpAct.triggered.connect(self.applySharpening)

        unsharpAct = QAction(QtGui.QIcon('img/unsharp.png'), 'Unsharp', self)
        unsharpAct.setStatusTip('Unsharp')
        unsharpAct.triggered.connect(self.applyUnsharpening)

        laplaceAct = QAction(QtGui.QIcon('img/laplace.png'), 'Laplace', self)
        laplaceAct.setStatusTip('Laplace')
        laplaceAct.triggered.connect(self.applyLaplace)

        separator4 = QAction(QtGui.QIcon('img/rotation.png'), 'Separator', self)
        separator4.setSeparator(True)

        watermarkAct = QAction(QtGui.QIcon('img/watermark.png'), 'Watermark', self)
        watermarkAct.setStatusTip('Watermark')
        watermarkAct.triggered.connect(self.showWatermarkPanel)

        self.toolbar = self.addToolBar('Tool Bar')
        self.toolbar.addAction(grayScaleAct)
        self.toolbar.addAction(flipAct)
        self.toolbar.addAction(separator1)
        self.toolbar.addAction(rotationAct)
        self.toolbar.addAction(cropAct)
        self.toolbar.addAction(overlayAct)
        self.toolbar.addAction(separator2)
        self.toolbar.addAction(invertAct)
        self.toolbar.addAction(textAct)
        self.toolbar.addAction(separator3)
        self.toolbar.addAction(sharpAct)
        self.toolbar.addAction(unsharpAct)
        self.toolbar.addAction(laplaceAct)
        self.toolbar.addAction(separator4)
        self.toolbar.addAction(watermarkAct)

        #toolbar settings
        self.toolbar.setMovable(False)
        self.toolbar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.toolbar.layout().setSpacing(7)
        self.toolbar.layout().setContentsMargins(6, 15, 4, 5)
        self.toolbar.setFixedHeight(40)
        self.toolbar.setStyleSheet("background:#FFFCE3")
        self.toolbar.setEnabled(False)

    
    def createMenuBar(self):
        menuBar=QMenuBar(self)
        #file
        fileMenu=QMenu("&File",self)
        
        openAct = QAction(QtGui.QIcon('img/open.png'), '&Open', self)
        openAct.setShortcut('Ctrl+O')
        openAct.setStatusTip('Open File')
        openAct.triggered.connect(self.openFileChooser)
        fileMenu.addAction(openAct)
        
        self.saveAct = QAction(QtGui.QIcon('img/save.png'), '&Save', self)
        self.saveAct.setShortcut('Ctrl+S')
        self.saveAct.setStatusTip('Save Image')
        self.saveAct.triggered.connect(self.saveFileChooser)
        self.saveAct.setEnabled(False)
        fileMenu.addAction(self.saveAct)

        exitAct = QAction(QtGui.QIcon('img/exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(QtWidgets.qApp.quit)
        fileMenu.addAction(exitAct)

        #edit
        editMenu=QMenu("&Edit",self)

        self.undoAct = QAction(QtGui.QIcon('img/undo.png'), '&Undo...', self)
        self.undoAct.setShortcut('Ctrl+Z')
        self.undoAct.setStatusTip('Undo...')
        self.undoAct.triggered.connect(self.performUndo)
        self.undoAct.setEnabled(False)
        editMenu.addAction(self.undoAct)
        

        self.redoAct = QAction(QtGui.QIcon('img/redo.png'), '&Redo...', self)
        self.redoAct.setShortcut('Ctrl+Y')
        self.redoAct.setStatusTip('Redo...')
        self.redoAct.triggered.connect(self.performRedo)
        self.redoAct.setEnabled(False)
        editMenu.addAction(self.redoAct)
        editMenu.addSeparator()

        self.brightnessAct = QAction(QtGui.QIcon('img/brightness.png'), '&Brightness', self)
        self.brightnessAct.setShortcut('Ctrl+B')
        self.brightnessAct.setStatusTip('Set Brightness')
        self.brightnessAct.triggered.connect(self.createBrightnessWindow)
        self.brightnessAct.setEnabled(False)
        editMenu.addAction(self.brightnessAct)

        self.contrastAct = QAction(QtGui.QIcon('img/contrast.png'), '&Contrast', self)
        self.contrastAct.setShortcut('Ctrl+C')
        self.contrastAct.setStatusTip('Set Contrast')
        self.contrastAct.triggered.connect(self.createContrastWindow)
        self.contrastAct.setEnabled(False)
        editMenu.addAction(self.contrastAct)
        editMenu.addSeparator()

        self.resizeAct = QAction(QtGui.QIcon('img/resize.png'), '&Resize', self)
        self.resizeAct.setShortcut('Ctrl+R')
        self.resizeAct.setStatusTip('Resize image')
        self.resizeAct.triggered.connect(self.createResizeWindow)
        self.resizeAct.setEnabled(False)
        editMenu.addAction(self.resizeAct)

        #View
        viewMenu=QMenu("&View",self)

        self.zoomInAct = QAction(QtGui.QIcon('img/zoom-in.png'), '&Zoom In', self)
        self.zoomInAct.setStatusTip('Zoom In')
        self.zoomInAct.setShortcut('Ctrl+K')
        self.zoomInAct.triggered.connect(self.performZoomIn)
        self.zoomInAct.setEnabled(False)
        viewMenu.addAction(self.zoomInAct)

        self.zoomOutAct = QAction(QtGui.QIcon('img/zoom-out.png'), '&Zoom Out', self)
        self.zoomOutAct.setStatusTip('Zoom Out')
        self.zoomOutAct.setShortcut('Ctrl+L')
        self.zoomOutAct.triggered.connect(self.performZoomOut)
        self.zoomOutAct.setEnabled(False)
        viewMenu.addAction(self.zoomOutAct)
        viewMenu.addSeparator()

        #transform
        transformMenu=QMenu("&Transform",self)
        self.blurMenu = QMenu('&Smoothing', self)
        self.blurMenu.setStatusTip('Smoothing')
        self.blurMenu.setEnabled(False)
        transformMenu.addMenu(self.blurMenu)

        self.gaussianBlurTransformAct = QAction(QtGui.QIcon('img/guassianBlur.png'), '&Guassian Blur', self)
        self.gaussianBlurTransformAct.setStatusTip('Guassian Blur')
        self.gaussianBlurTransformAct.triggered.connect(self.createGuassianBlurWindow)
        #self.gaussianSmoothingTransformAct.setEnabled(False)
        self.blurMenu.addAction(self.gaussianBlurTransformAct)

        self.boxBlurTransformAct = QAction(QtGui.QIcon('img/boxBlur.png'), '&Box Blur', self)
        self.boxBlurTransformAct.setStatusTip('Box Blur')
        self.boxBlurTransformAct.triggered.connect(self.applyBoxBlur)
        #self.boxBlurTransformAct.setEnabled(False)
        self.blurMenu.addAction(self.boxBlurTransformAct)

        self.verticalMotionBlurTransformAct = QAction(QtGui.QIcon('img/verticalMotionBlur.png'), '&Vertical Motion Blur', self)
        self.verticalMotionBlurTransformAct.setStatusTip('Vertical Motion Blur')
        self.verticalMotionBlurTransformAct.triggered.connect(self.createVerticalMotionBlurWindow)
        #self.verticalMotionBlurTransformAct.setEnabled(False)
        self.blurMenu.addAction(self.verticalMotionBlurTransformAct)

        self.horizontalMotionBlurTransformAct = QAction(QtGui.QIcon('img/horizontalMotionBlur.png'), '&Horizontal Motion Blur', self)
        self.horizontalMotionBlurTransformAct.setStatusTip('Horizontal Motion Blur')
        self.horizontalMotionBlurTransformAct.triggered.connect(self.createHorizontalMotionBlurWindow)
        #self.horizontalMotionBlurTransformAct.setEnabled(False)
        self.blurMenu.addAction(self.horizontalMotionBlurTransformAct)

        #border
        self.borderAct = QAction(QtGui.QIcon('img/border.png'), '&Border', self)
        self.borderAct.setStatusTip('Border')
        self.borderAct.setShortcut('Ctrl+B')
        self.borderAct.triggered.connect(self.createBorderDialog)
        self.borderAct.setEnabled(False)
        transformMenu.addAction(self.borderAct)

        self.setMenuBar(menuBar)
        menuBar.addMenu(fileMenu)
        menuBar.addMenu(editMenu)
        menuBar.addMenu(viewMenu)
        menuBar.addMenu(transformMenu)

    def performZoomIn(self):
        self.worker=Worker()
        self.worker.setOperation(22)
        self.worker.setTmApplication(self)
        self.worker.signal.connect(self.taskFinished)
        self.worker.start()
        self.showLoader()


    def performZoomOut(self):
        self.worker=Worker()
        self.worker.setOperation(23)
        self.worker.setTmApplication(self)
        self.worker.signal.connect(self.taskFinished)
        self.worker.start()
        self.showLoader()

    def performUndo(self):
        undoStack=self.images["undoStack"]
        redoStack=self.images["redoStack"]
        redoStack.append(undoStack.pop())
        imagePath=undoStack[len(undoStack)-1]
        self.images["path"]=imagePath
        self.images["filterImageName"]=""
        self.update()

    def performRedo(self):
        undoStack=self.images["undoStack"]
        redoStack=self.images["redoStack"]
        undoStack.append(redoStack.pop())
        imagePath=undoStack[len(undoStack)-1]
        self.images["path"]=imagePath
        self.images["filterImageName"]=""
        self.update()

    def resetResizeValues(self):
        self.resizeHeightTextArea.setText("0")
        self.resizeWidthTextArea.setText("0")

    def setBrightnessFactor(self):
        self.brightnessFactor=self.brightnessSlider.value()
    
    def setContrastFactor(self):
        self.contrastFactor=self.contrastSlider.value()

    def resizeImage(self):
        self.worker.setTmApplication(self)
        self.worker.setOperation(12)
        self.worker.signal.connect(self.taskFinished)
        self.resizeDialog.close()
        self.worker.start()
        self.showLoader()

    def setBrightness(self):
        self.worker.setTmApplication(self)
        self.worker.setOperation(2)
        self.worker.signal.connect(self.taskFinished)
        self.brightnessDialog.close()
        self.worker.start()
        self.showLoader()

    def setContrast(self):
        self.worker.setTmApplication(self)
        self.worker.setOperation(3)
        self.worker.signal.connect(self.taskFinished)
        self.contrastDialog.close()
        self.worker.start()
        self.showLoader()

    def createBorderDialog(self):
        #open window for border setup
        self.normalBorderPanel1Activator=False
        self.normalBorderPanel2Activator=False

        self.replicateBorderPanel1Activator=False
        self.replicateBorderPanel2Activator=False

        self.replicate_standardRadioButton=None
        self.replicate_customRadioButton=None

        self.normal_standardRadioButton=None
        self.normal_customRadioButton=None

        self.borderDialog=QDialog(self)
        self.borderDialog.resize(300,225)
        self.borderDialog.setWindowTitle("Set Border")

        borderTypeLabel=QLabel(self.borderDialog)
        borderTypeLabel.setText("Border-Type : ")
        borderTypeLabel.setGeometry(50,10,100,50)
        borderTypeLabel.show()

        self.borderTypeList=QComboBox(self.borderDialog)
        self.borderTypeList.addItem("Select",-1)
        self.borderTypeList.addItem("Normal",0)
        self.borderTypeList.addItem("Replicate",1)
        self.borderTypeList.activated.connect(self.showBorderPanels)
        self.borderTypeList.setEditable(False)
        self.borderTypeList.setGeometry(130,25,100,20)
        self.borderTypeList.show()
        self.borderDialog.exec_()

    
    def showNormalStandardBorderPanel(self):
        self.normalBorderPanel1Activator=True
        self.hideNormalCustomBorderPanel()
        self.normal_borderThicknessLabel.show()
        self.normal_borderThicknessTextArea.show()
        self.normal_borderThicknessPixelLabel.show()
        self.normal_borderColorLabel.show()
        self.normal_borderColorButton.show()
        self.normal_standardOKButton.show()
        self.normal_standardCancelButton.show()

    def showNormalCustomBorderPanel(self):
        self.normalBorderPanel2Activator=True
        self.hideNormalStandardBorderPanel()
        self.normal_borderTopLabel.show()
        self.normal_borderTopTextArea.show()
        self.normal_borderBottomLabel.show()
        self.normal_borderBottomTextArea.show()
        self.normal_borderLeftLabel.show()
        self.normal_borderLeftTextArea.show()
        self.normal_borderRightLabel.show()
        self.normal_borderRightTextArea.show()
        self.normal_customBorderColorLabel.show()
        self.normal_customBorderColorButton.show()
        self.normal_customOKButton.show()
        self.normal_customCancelButton.show()
    
    def hideNormalCustomBorderPanel(self):
        self.normalBorderPanel2Activator=False
        self.normal_borderTopLabel.hide()
        self.normal_borderTopTextArea.hide()
        self.normal_borderBottomLabel.hide()
        self.normal_borderBottomTextArea.hide()
        self.normal_borderLeftLabel.hide()
        self.normal_borderLeftTextArea.hide()
        self.normal_borderRightLabel.hide()
        self.normal_borderRightTextArea.hide()
        self.normal_customBorderColorLabel.hide()
        self.normal_customBorderColorButton.hide()
        self.normal_customOKButton.hide()
        self.normal_customCancelButton.hide()

    def hideNormalStandardBorderPanel(self):
        self.normalBorderPanel1Activator=False
        self.normal_borderThicknessLabel.hide()
        self.normal_borderThicknessTextArea.hide()
        self.normal_borderThicknessPixelLabel.hide()
        self.normal_borderColorLabel.hide()
        self.normal_borderColorButton.hide()
        self.normal_standardOKButton.hide()
        self.normal_standardCancelButton.hide()

    
    def showReplicateStandardBorderPanel(self):
        self.replicateBorderPanel1Activator=True
        self.hideReplicateCustomBorderPanel()
        self.replicate_borderThicknessLabel.show()
        self.replicate_borderThicknessTextArea.show()
        self.replicate_borderThicknessPixelLabel.show()
        self.replicate_standardOKButton.show()
        self.replicate_standardCancelButton.show()

    def hideReplicateStandardBorderPanel(self):
        self.replicateBorderPanel1Activator=False
        self.replicate_borderThicknessLabel.hide()
        self.replicate_borderThicknessTextArea.hide()
        self.replicate_borderThicknessPixelLabel.hide()
        self.replicate_standardOKButton.hide()
        self.replicate_standardCancelButton.hide()

    def showReplicateCustomBorderPanel(self):
        self.replicateBorderPanel2Activator=True
        self.hideReplicateStandardBorderPanel()
        self.replicate_borderTopLabel.show()
        self.replicate_borderTopTextArea.show()
        self.replicate_borderBottomLabel.show()
        self.replicate_borderBottomTextArea.show()
        self.replicate_borderLeftLabel.show()
        self.replicate_borderLeftTextArea.show()
        self.replicate_borderRightLabel.show()
        self.replicate_borderRightTextArea.show()
        self.replicate_customOKButton.show()
        self.replicate_customCancelButton.show()

    def hideReplicateCustomBorderPanel(self):
        self.replicateBorderPanel2Activator=False
        self.replicate_borderTopLabel.hide()
        self.replicate_borderTopTextArea.hide()
        self.replicate_borderBottomLabel.hide()
        self.replicate_borderBottomTextArea.hide()
        self.replicate_borderLeftLabel.hide()
        self.replicate_borderLeftTextArea.hide()
        self.replicate_borderRightLabel.hide()
        self.replicate_borderRightTextArea.hide()
        self.replicate_customOKButton.hide()
        self.replicate_customCancelButton.hide()

    
    def resetBorderPanels(self,index):
        if index==1:
            if self.replicateBorderPanel1Activator:
                self.hideReplicateStandardBorderPanel()
            if self.replicateBorderPanel2Activator:
                self.hideReplicateCustomBorderPanel()

            if self.replicate_standardRadioButton!=None:
                self.replicate_standardRadioButton.hide()
            if self.replicate_customRadioButton!=None:
                self.replicate_customRadioButton.hide()
                self.separatorLine2.hide()

        elif index==2:
            if self.normalBorderPanel1Activator:
                self.hideNormalStandardBorderPanel()
            if self.normalBorderPanel2Activator:
                self.hideNormalCustomBorderPanel()
            if self.normal_standardRadioButton!=None:
                self.normal_standardRadioButton.hide()
            if self.normal_customRadioButton!=None:
                self.normal_customRadioButton.hide()
                self.separatorLine1.hide()

    def open_normal_standard_color_chooser(self):
        color=QColorDialog.getColor()
        if color.isValid():
            borderColor=color.name()
            self.normal_borderColorButton.setText(borderColor)        

    def validate_normal_standard_border_factors(self):                
        color=self.normal_borderColorButton.text()
        errorMessage=""
        hasError=False
        try:
            thickness=int(self.normal_borderThicknessTextArea.text())
        except:
            errorMessage+="Invalid thickness input. \r\n"
            hasError=True
        errorDialog=QtWidgets.QErrorMessage(self.borderDialog)
        if color.startswith("Choose"):
            hasError=True
            errorMessage+="Invalid color selection. \r\n"
        if hasError:
            errorDialog.showMessage(errorMessage)
            errorDialog.setWindowTitle(f"Invalid Input Error")
        else: 
            operationString=dict()
            operationString["thickness"]=thickness
            operationString["isTuple"]=False
            operationString["color"]=color
            operationString["border-type"]="normal_standard"
    
            self.worker.setTmApplication(self)
            self.worker.setOperation(26)
            self.worker.setOperationString(operationString)
            self.worker.signal.connect(self.taskFinished)
            self.worker.start()
            self.showLoader()
    
    def open_normal_custom_color_chooser(self):
        color=QColorDialog.getColor()
        if color.isValid():
            borderColor=color.name()
            self.normal_customBorderColorButton.setText(borderColor)        
            #done done
    
    def validate_normal_custom_border_factors(self):
        color=self.normal_customBorderColorButton.text()
        hasError=False
        errorMessage=""
        try:
            top=int(self.normal_borderTopTextArea.text())
        except:
            errorMessage+="Invalid top value input. \r\n"
            hasError=True
        try:
            bottom=int(self.normal_borderBottomTextArea.text())
        except:
            errorMessage+="Invalid bottom value input. \r\n"
            hasError=True
        try:
            left=int(self.normal_borderLeftTextArea.text())
        except:
            errorMessage+="Invalid left value input. \r\n"
            hasError=True
        try:
            right=int(self.normal_borderRightTextArea.text())
        except:
            errorMessage+="Invalid right value input. \r\n"
            hasError=True
        if len(color)==0 or color.startswith("Choose..."):
            errorMessage="Invalid color selection. \r\n"
            hasError=True
        if hasError:
            errorDialog=QtWidgets.QErrorMessage(self.borderDialog)
            errorDialog.showMessage(errorMessage)
            errorDialog.showWindowTitle("Invalid Input Error")
        else:
            operationString=dict()
            thickness=list()
            thickness.append(top)
            thickness.append(bottom)
            thickness.append(left)
            thickness.append(right)
            operationString["thickness"]=thickness
            operationString["isTuple"]=True
            operationString["color"]=color
            operationString["border-type"]="normal_custom"
    
            self.worker.setTmApplication(self)
            self.worker.setOperation(26)
            self.worker.setOperationString(operationString)
            self.worker.signal.connect(self.taskFinished)
            self.worker.start()
            self.showLoader()

    def validate_replicate_standard_border_parameters(self):
        hasError=False
        errorMessage=""
        try:
            thickness=int(self.replicate_borderThicknessTextArea.text())
        except:
            errorMessage+="Invalid thickness input. \r\n"
            hasError=True
        if hasError:
            errorDialog=QtWidgets.QErrorMessage(self.borderDialog)
            errorDialog.showMessage(errorMessage)
            errorDialog.showWindowTitle("Invalid Input Error")
        else:
            operationString=dict()
            operationString["thickness"]=thickness
            operationString["isTuple"]=True
            operationString["border-type"]="replicate_standard"
    
            self.worker.setTmApplication(self)
            self.worker.setOperation(27)
            self.worker.setOperationString(operationString)
            self.worker.signal.connect(self.taskFinished)
            self.worker.start()
            self.showLoader()
    
    def validate_replicate_custom_border_parameters(self):
        hasError=False
        errorMessage=""
        try:
            top=int(self.replicate_borderTopTextArea.text())
        except:
            errorMessage+="Invalid top value input. \r\n"
            hasError=True
        try:
            bottom=int(self.replicate_borderBottomTextArea.text())
        except:
            errorMessage+="Invalid bottom value input. \r\n"
            hasError=True
        try:
            left=int(self.replicate_borderLeftTextArea.text())
        except:
            errorMessage+="Invalid left value input. \r\n"
            hasError=True
        try:
            right=int(self.replicate_borderRightTextArea.text())
        except:
            errorMessage+="Invalid right value input. \r\n"
            hasError=True
        
        if hasError:
            errorDialog=QtWidgets.QErrorMessage(self.borderDialog)
            errorDialog.showMessage(errorMessage)
            errorDialog.showWindowTitle("Invalid Input Error")
        else:
            operationString=dict()
            thickness=list()
            thickness.append(top)
            thickness.append(bottom)
            thickness.append(left)
            thickness.append(right)
            operationString["thickness"]=thickness
            operationString["isTuple"]=True
            operationString["border-type"]="replicate_custom"
    
            self.worker.setTmApplication(self)
            self.worker.setOperation(27)
            self.worker.setOperationString(operationString)
            self.worker.signal.connect(self.taskFinished)
            self.worker.start()
            self.showLoader()


    def showBorderPanels(self,index):
        if index==1:
            self.resetBorderPanels(index)
            #normal standard border
            self.normalBorderPanel1Activator=True
            self.normal_standardRadioButton=QRadioButton(self.borderDialog)
            self.normal_standardRadioButton.setText("Standard")
            self.normal_standardRadioButton.setChecked(True)
            self.normal_standardRadioButton.setGeometry(50,50,100,50)
            self.normal_standardRadioButton.clicked.connect(self.showNormalStandardBorderPanel)
            self.normal_standardRadioButton.show()

            self.normal_customRadioButton=QRadioButton(self.borderDialog)
            self.normal_customRadioButton.setText("Custom")
            self.normal_customRadioButton.setGeometry(190,50,100,50)
            self.normal_customRadioButton.clicked.connect(self.showNormalCustomBorderPanel)
            self.normal_customRadioButton.show()

            #separator line
            self.separatorLine1=QFrame(self.borderDialog)
            self.separatorLine1.setFrameShape(QFrame.HLine)
            self.separatorLine1.setFrameShadow(QFrame.Sunken)
            self.separatorLine1.setGeometry(0,70,300,50)
            self.separatorLine1.show()

            self.normal_borderThicknessLabel=QLabel(self.borderDialog)
            self.normal_borderThicknessLabel.setText("Thickness : ")
            self.normal_borderThicknessLabel.setGeometry(50,100,150,50)
            self.normal_borderThicknessLabel.show()

            self.normal_borderThicknessTextArea=QLineEdit("",self.borderDialog)
            self.normal_borderThicknessTextArea.setGeometry(115,115,70,20)
            self.normal_borderThicknessTextArea.show()

            self.normal_borderThicknessPixelLabel=QLabel(self.borderDialog)
            self.normal_borderThicknessPixelLabel.setText("Pixels")
            self.normal_borderThicknessPixelLabel.setGeometry(200,117,40,15)
            self.normal_borderThicknessPixelLabel.setStyleSheet("background:white;")
            self.normal_borderThicknessPixelLabel.setAlignment(QtCore.Qt.AlignCenter)
            self.normal_borderThicknessPixelLabel.show()

            self.normal_borderColorLabel=QLabel(self.borderDialog)
            self.normal_borderColorLabel.setText("Color : ")
            self.normal_borderColorLabel.setGeometry(50,135,150,50)
            self.normal_borderColorLabel.show()

            self.normal_borderColorButton=QPushButton("Choose...",self.borderDialog)
            self.normal_borderColorButton.setIcon(QIcon("img/choose.png"))
            self.normal_borderColorButton.clicked.connect(self.open_normal_standard_color_chooser)
            self.normal_borderColorButton.setGeometry(113,150,100,23)
            self.normal_borderColorButton.show()

            self.normal_standardOKButton=QPushButton("OK",self.borderDialog)
            self.normal_standardOKButton.move(70,190)
            self.normal_standardOKButton.setIcon(QIcon("img/ok.png"))
            self.normal_standardOKButton.clicked.connect(self.validate_normal_standard_border_factors)
            self.normal_standardOKButton.show()

            self.normal_standardCancelButton=QPushButton("Cancel",self.borderDialog)
            self.normal_standardCancelButton.move(170,190)
            self.normal_standardCancelButton.setIcon(QIcon("img/cancel.png"))
            self.normal_standardCancelButton.clicked.connect(self.borderDialog.close)
            self.normal_standardCancelButton.show()

            #normal custom border

            self.normal_borderTopLabel=QLabel(self.borderDialog)
            self.normal_borderTopLabel.setText("Top : ")
            self.normal_borderTopLabel.setGeometry(30,90,150,50)
            self.normal_borderTopLabel.hide()

            self.normal_borderTopTextArea=QLineEdit("",self.borderDialog)
            self.normal_borderTopTextArea.setGeometry(70,107,50,18)
            self.normal_borderTopTextArea.hide()

            self.normal_borderBottomLabel=QLabel(self.borderDialog)
            self.normal_borderBottomLabel.setText("Bottom : ")
            self.normal_borderBottomLabel.setGeometry(160,90,150,50)
            self.normal_borderBottomLabel.hide()

            self.normal_borderBottomTextArea=QLineEdit("",self.borderDialog)
            self.normal_borderBottomTextArea.setGeometry(210,107,50,18)
            self.normal_borderBottomTextArea.hide()

            self.normal_borderLeftLabel=QLabel(self.borderDialog)
            self.normal_borderLeftLabel.setText("Left : ")
            self.normal_borderLeftLabel.setGeometry(30,115,150,50)
            self.normal_borderLeftLabel.hide()

            self.normal_borderLeftTextArea=QLineEdit("",self.borderDialog)
            self.normal_borderLeftTextArea.setGeometry(70,132,50,18)
            self.normal_borderLeftTextArea.hide()

            self.normal_borderRightLabel=QLabel(self.borderDialog)
            self.normal_borderRightLabel.setText("Right : ")
            self.normal_borderRightLabel.setGeometry(160,115,150,50)
            self.normal_borderRightLabel.hide()

            self.normal_borderRightTextArea=QLineEdit("",self.borderDialog)
            self.normal_borderRightTextArea.setGeometry(210,132,50,18)
            self.normal_borderRightTextArea.hide()

            self.normal_customBorderColorLabel=QLabel(self.borderDialog)
            self.normal_customBorderColorLabel.setText("Color : ")
            self.normal_customBorderColorLabel.setGeometry(30,143,150,50)
            self.normal_customBorderColorLabel.hide()

            self.normal_customBorderColorButton=QPushButton("Choose...",self.borderDialog)
            self.normal_customBorderColorButton.setIcon(QIcon("img/choose.png"))
            self.normal_customBorderColorButton.clicked.connect(self.open_normal_custom_color_chooser)
            self.normal_customBorderColorButton.setGeometry(70,158,100,20)
            self.normal_customBorderColorButton.hide()

            self.normal_customOKButton=QPushButton("OK",self.borderDialog)
            self.normal_customOKButton.move(70,190)
            self.normal_customOKButton.setIcon(QIcon("img/ok.png"))
            self.normal_customOKButton.clicked.connect(self.validate_normal_custom_border_factors)
            self.normal_customOKButton.hide()

            self.normal_customCancelButton=QPushButton("Cancel",self.borderDialog)
            self.normal_customCancelButton.move(170,190)
            self.normal_customCancelButton.setIcon(QIcon("img/cancel.png"))
            self.normal_customCancelButton.clicked.connect(self.borderDialog.close)
            self.normal_customCancelButton.hide()

        elif index==2:
            self.resetBorderPanels(index)
            #replicate standard border
            self.replicateBorderPanel1Activator=True
            self.replicate_standardRadioButton=QRadioButton(self.borderDialog)
            self.replicate_standardRadioButton.setText("Standard")
            self.replicate_standardRadioButton.setChecked(True)
            self.replicate_standardRadioButton.setGeometry(50,50,100,50)
            self.replicate_standardRadioButton.clicked.connect(self.showReplicateStandardBorderPanel)
            self.replicate_standardRadioButton.show()

            self.replicate_customRadioButton=QRadioButton(self.borderDialog)
            self.replicate_customRadioButton.setText("Custom")
            self.replicate_customRadioButton.setGeometry(190,50,100,50)
            self.replicate_customRadioButton.clicked.connect(self.showReplicateCustomBorderPanel)
            self.replicate_customRadioButton.show()

            #separator line
            self.separatorLine2=QFrame(self.borderDialog)
            self.separatorLine2.setFrameShape(QFrame.HLine)
            self.separatorLine2.setFrameShadow(QFrame.Sunken)
            self.separatorLine2.setGeometry(0,70,300,50)
            self.separatorLine2.show()

            self.replicate_borderThicknessLabel=QLabel(self.borderDialog)
            self.replicate_borderThicknessLabel.setText("Thickness : ")
            self.replicate_borderThicknessLabel.setGeometry(50,100,150,50)
            self.replicate_borderThicknessLabel.show()

            self.replicate_borderThicknessTextArea=QLineEdit("",self.borderDialog)
            self.replicate_borderThicknessTextArea.setGeometry(115,115,70,20)
            self.replicate_borderThicknessTextArea.show()

            self.replicate_borderThicknessPixelLabel=QLabel(self.borderDialog)
            self.replicate_borderThicknessPixelLabel.setText("Pixels")
            self.replicate_borderThicknessPixelLabel.setGeometry(200,117,40,15)
            self.replicate_borderThicknessPixelLabel.setStyleSheet("background:white;")
            self.replicate_borderThicknessPixelLabel.setAlignment(QtCore.Qt.AlignCenter)
            self.replicate_borderThicknessPixelLabel.show()

            self.replicate_standardOKButton=QPushButton("OK",self.borderDialog)
            self.replicate_standardOKButton.move(70,190)
            self.replicate_standardOKButton.setIcon(QIcon("img/ok.png"))
            self.replicate_standardOKButton.clicked.connect(self.validate_replicate_standard_border_parameters)
            self.replicate_standardOKButton.show()

            self.replicate_standardCancelButton=QPushButton("Cancel",self.borderDialog)
            self.replicate_standardCancelButton.move(170,190)
            self.replicate_standardCancelButton.setIcon(QIcon("img/cancel.png"))
            self.replicate_standardCancelButton.clicked.connect(self.borderDialog.close)
            self.replicate_standardCancelButton.show()

            #replicate custom border

            self.replicate_borderTopLabel=QLabel(self.borderDialog)
            self.replicate_borderTopLabel.setText("Top : ")
            self.replicate_borderTopLabel.setGeometry(30,90,150,50)
            self.replicate_borderTopLabel.hide()

            self.replicate_borderTopTextArea=QLineEdit("",self.borderDialog)
            self.replicate_borderTopTextArea.setGeometry(70,107,50,18)
            self.replicate_borderTopTextArea.hide()

            self.replicate_borderBottomLabel=QLabel(self.borderDialog)
            self.replicate_borderBottomLabel.setText("Bottom : ")
            self.replicate_borderBottomLabel.setGeometry(160,90,150,50)
            self.replicate_borderBottomLabel.hide()

            self.replicate_borderBottomTextArea=QLineEdit("",self.borderDialog)
            self.replicate_borderBottomTextArea.setGeometry(210,107,50,18)
            self.replicate_borderBottomTextArea.hide()

            self.replicate_borderLeftLabel=QLabel(self.borderDialog)
            self.replicate_borderLeftLabel.setText("Left : ")
            self.replicate_borderLeftLabel.setGeometry(30,130,150,50)
            self.replicate_borderLeftLabel.hide()

            self.replicate_borderLeftTextArea=QLineEdit("",self.borderDialog)
            self.replicate_borderLeftTextArea.setGeometry(70,147,50,18)
            self.replicate_borderLeftTextArea.hide()

            self.replicate_borderRightLabel=QLabel(self.borderDialog)
            self.replicate_borderRightLabel.setText("Right : ")
            self.replicate_borderRightLabel.setGeometry(160,130,150,50)
            self.replicate_borderRightLabel.hide()

            self.replicate_borderRightTextArea=QLineEdit("",self.borderDialog)
            self.replicate_borderRightTextArea.setGeometry(210,147,50,18)
            self.replicate_borderRightTextArea.hide()

            self.replicate_customOKButton=QPushButton("OK",self.borderDialog)
            self.replicate_customOKButton.move(70,190)
            self.replicate_customOKButton.setIcon(QIcon("img/ok.png"))
            self.replicate_customOKButton.clicked.connect(self.validate_replicate_custom_border_parameters)
            self.replicate_customOKButton.hide()

            self.replicate_customCancelButton=QPushButton("Cancel",self.borderDialog)
            self.replicate_customCancelButton.move(170,190)
            self.replicate_customCancelButton.setIcon(QIcon("img/cancel.png"))
            self.replicate_customCancelButton.clicked.connect(self.borderDialog.close)
            self.replicate_customCancelButton.hide()


    def createBrightnessWindow(self):
        #open window for brightness setup
        self.brightnessDialog=QDialog(self)
        self.brightnessDialog.resize(300,150)
        self.brightnessDialog.setWindowTitle("Set Brightness")

        label=QLabel(self.brightnessDialog)
        label.setText("Brightness: ")
        label.setGeometry(60,16,100,30)

        self.brightnessSlider=QSlider(Qt.Horizontal,self.brightnessDialog)
        self.brightnessSlider.setFocusPolicy(Qt.NoFocus)
        self.brightnessSlider.setTickPosition(QSlider.TicksAbove)
        self.brightnessSlider.setTickInterval(10)
        self.brightnessSlider.setSingleStep(10)
        self.brightnessSlider.setValue(50)
        self.brightnessSlider.setGeometry(60,51,170,50)
        self.brightnessSlider.valueChanged.connect(self.setBrightnessFactor)

        self.brightnessbutton=QPushButton("OK",self.brightnessDialog)
        self.brightnessbutton.move(110,111)
        self.brightnessbutton.clicked.connect(self.setBrightness)

        self.brightnessDialog.exec_()
    

    def createResizeWindow(self):

        imageSize=str(self.images["size"])
        imageHeight=str(self.images["height"])
        imageWidth=str(self.images["width"])

        self.resizeDialog=QDialog(self)
        self.resizeDialog.resize(400,200)
        self.resizeDialog.setWindowTitle("Resize Image")

        sizeTitleLabel=QLabel(self.resizeDialog)
        sizeTitleLabel.setText("Image Size: ")
        sizeTitleLabel.setGeometry(40,16,100,30)

        sizeLabel=QLabel(self.resizeDialog)
        sizeLabel.setText(imageSize+" MB")
        sizeLabel.setGeometry(110,16,100,30)        

        dimensionsTitleLabel=QLabel(self.resizeDialog)
        dimensionsTitleLabel.setText("Dimensions: ")
        dimensionsTitleLabel.setGeometry(40,46,100,30)

        dimensionsLabel=QLabel(self.resizeDialog)
        dimensionsLabel.setText(imageHeight+"x"+imageWidth)
        dimensionsLabel.setGeometry(110,46,100,30)

        heightTitleLabel=QLabel(self.resizeDialog)
        heightTitleLabel.setText("Height: ")
        heightTitleLabel.setGeometry(40,90,100,30)

        self.resizeHeightTextArea=QLineEdit(self.resizeDialog)
        self.resizeHeightTextArea.setText(imageHeight)
        self.resizeHeightTextArea.setGeometry(90,95,80,20)
        self.resizeHeightTextArea.textChanged.connect(self.updateResizeParameters)

        pixelLabel1=QLabel(self.resizeDialog)
        pixelLabel1.setText("Pixels")
        pixelLabel1.setGeometry(190,95,80,20)
        pixelLabel1.setStyleSheet("background-color:white;")
        pixelLabel1.setAlignment(QtCore.Qt.AlignCenter)

        widthTitleLabel=QLabel(self.resizeDialog)
        widthTitleLabel.setText("Width: ")
        widthTitleLabel.setGeometry(40,120,100,30)

        self.resizeWidthTextArea=QLineEdit(self.resizeDialog)
        self.resizeWidthTextArea.setText(imageWidth)
        self.resizeWidthTextArea.setGeometry(90,125,80,20)
        self.resizeWidthTextArea.textChanged.connect(self.updateResizeParameters)

        pixelLabel2=QLabel(self.resizeDialog)
        pixelLabel2.setText("Pixels")
        pixelLabel2.setGeometry(190,125,80,20)
        pixelLabel2.setStyleSheet("background-color:white;")
        pixelLabel2.setAlignment(QtCore.Qt.AlignCenter)

        self.resizeOKButton=QPushButton("OK",self.resizeDialog)
        self.resizeOKButton.move(310,21)
        self.resizeOKButton.clicked.connect(self.resizeImage)

        self.resizeCancelButton=QPushButton("Cancel",self.resizeDialog)
        self.resizeCancelButton.move(310,55)
        self.resizeCancelButton.clicked.connect(self.resizeDialog.close)

        self.resizeResetButton=QPushButton("Reset",self.resizeDialog)
        self.resizeResetButton.move(310,81)
        self.resizeResetButton.clicked.connect(self.resetResizeValues)

        self.resizeDialog.exec_()
    
    def applyBoxBlur(self):
        self.worker.setTmApplication(self)
        self.worker.setOperation(16)
        self.worker.signal.connect(self.taskFinished)
        self.worker.start()
        self.showLoader()
    
    def applyVerticalMotionBlur(self):
        radius=10
        if self.verticalMotionBlur10RadioButton.isChecked():
            radius=10
        elif self.verticalMotionBlur20RadioButton.isChecked():
            radius=20
        elif self.verticalMotionBlur50RadioButton.isChecked():
            radius=50
        elif self.verticalMotionBlur100RadioButton.isChecked():
            radius=100

        self.worker.setTmApplication(self)
        self.worker.setOperation(14)
        self.worker.setRadius(radius)
        self.verticalMotionBlurDialog.close()
        self.worker.signal.connect(self.taskFinished)
        self.worker.start()
        self.showLoader()
    
    def applyLaplace(self):
        self.worker.setTmApplication(self)
        self.worker.setOperation(20)
        self.worker.signal.connect(self.taskFinished)
        self.worker.start()
        self.showLoader()
    
    def applyUnsharpening(self):
        self.worker.setTmApplication(self)
        self.worker.setOperation(19)
        self.worker.signal.connect(self.taskFinished)
        self.worker.start()
        self.showLoader()

    def applySharpening(self):
        self.worker.setTmApplication(self)
        self.worker.setOperation(18)
        self.worker.signal.connect(self.taskFinished)
        self.worker.start()
        self.showLoader()

    def applyInvert(self):
        self.worker.setTmApplication(self)
        self.worker.setOperation(17)
        self.worker.signal.connect(self.taskFinished)
        self.worker.start()
        self.showLoader()

    def applyGuassianBlur(self):
        radius=2
        if self.gaussian20RadioButton.isChecked():
            radius=2
        elif self.gaussian40RadioButton.isChecked():
            radius=4
        elif self.gaussian60RadioButton.isChecked():
            radius=6

        self.worker.setTmApplication(self)
        self.worker.setOperation(13)
        self.worker.setRadius(radius)
        self.guassianBlurDialog.close()
        self.worker.signal.connect(self.taskFinished)
        self.worker.start()
        self.showLoader()

    def showGaussianPreview(self):
        if self.gaussian20RadioButton.isChecked():
            self.gaussianBlurPreview.setPixmap(QPixmap("img/previews/gaussian20.jpg"))
        elif self.gaussian40RadioButton.isChecked():
            self.gaussianBlurPreview.setPixmap(QPixmap("img/previews/gaussian40.jpg"))
        elif self.gaussian60RadioButton.isChecked():
            self.gaussianBlurPreview.setPixmap(QPixmap("img/previews/gaussian60.jpg"))            
        
    def showVerticalMotionBlurPreview(self):
        if self.verticalMotionBlur10RadioButton.isChecked():
            self.verticalMotionBlurPreview.setPixmap(QPixmap("img/previews/carVerticalMotion10.jpg"))
        elif self.verticalMotionBlur20RadioButton.isChecked():
            self.verticalMotionBlurPreview.setPixmap(QPixmap("img/previews/carVerticalMotion20.jpg"))       
        elif self.verticalMotionBlur50RadioButton.isChecked():
           self.verticalMotionBlurPreview.setPixmap(QPixmap("img/previews/carVerticalMotion50.jpg"))                   
        elif self.verticalMotionBlur100RadioButton.isChecked():
            self.verticalMotionBlurPreview.setPixmap(QPixmap("img/previews/carVerticalMotion100.jpg"))       
    
    def showHorizontalMotionBlurPreview(self):
        if self.horizontalMotionBlur10RadioButton.isChecked():
            self.horizontalMotionBlurPreview.setPixmap(QPixmap("img/previews/mountainHorizontalMotion10.jpg"))
        elif self.horizontalMotionBlur20RadioButton.isChecked():
            self.horizontalMotionBlurPreview.setPixmap(QPixmap("img/previews/mountainHorizontalMotion20.jpg"))
        elif self.horizontalMotionBlur50RadioButton.isChecked():
            self.horizontalMotionBlurPreview.setPixmap(QPixmap("img/previews/mountainHorizontalMotion50.jpg"))
        elif self.horizontalMotionBlur100RadioButton.isChecked():
            self.horizontalMotionBlurPreview.setPixmap(QPixmap("img/previews/mountainHorizontalMotion100.jpg"))
    
    def applyHorizontalMotionBlur(self):
        radius=10
        if self.horizontalMotionBlur10RadioButton.isChecked():
            radius=10
        elif self.horizontalMotionBlur20RadioButton.isChecked():
            radius=20
        elif self.horizontalMotionBlur50RadioButton.isChecked():
            radius=50
        elif self.horizontalMotionBlur100RadioButton.isChecked():
            radius=100
        
        self.worker.setTmApplication(self)
        self.worker.setOperation(15)
        self.worker.setRadius(radius)
        self.horizontalMotionBlurDialog.close()
        self.worker.signal.connect(self.taskFinished)
        self.worker.start()
        self.showLoader()

    def createHorizontalMotionBlurWindow(self):
        #open window for guassian blur setup
        self.horizontalMotionBlurDialog=QDialog(self)
        self.horizontalMotionBlurDialog.resize(450,320)
        self.horizontalMotionBlurDialog.setWindowTitle("Set Motion Blur (%) - Horizontally")

        self.horizontalMotionBlurPreview=QLabel(self.horizontalMotionBlurDialog)
        self.horizontalMotionBlurPreview.setPixmap(QPixmap("img/previews/mountainHorizontalMotion10.jpg"))
        self.horizontalMotionBlurPreview.setGeometry(15,5,420,200)        
        self.horizontalMotionBlurPreview.setStyleSheet("border:1px solid black;")
        
        self.horizontalMotionBlur10RadioButton=QRadioButton(self.horizontalMotionBlurDialog)
        self.horizontalMotionBlur10RadioButton.setGeometry(55,205,80,80)
        self.horizontalMotionBlur10RadioButton.setText("10% Blur")
        self.horizontalMotionBlur10RadioButton.setChecked(True)
        self.horizontalMotionBlur10RadioButton.clicked.connect(self.showHorizontalMotionBlurPreview)
        self.horizontalMotionBlur10RadioButton.show()

        self.horizontalMotionBlur20RadioButton=QRadioButton(self.horizontalMotionBlurDialog)
        self.horizontalMotionBlur20RadioButton.setGeometry(55+80+20,205,80,80)
        self.horizontalMotionBlur20RadioButton.setText("20% Blur")
        self.horizontalMotionBlur20RadioButton.clicked.connect(self.showHorizontalMotionBlurPreview)
        self.horizontalMotionBlur20RadioButton.show()

        self.horizontalMotionBlur50RadioButton=QRadioButton(self.horizontalMotionBlurDialog)
        self.horizontalMotionBlur50RadioButton.setGeometry(55+80+55+55+15,205,80,80)
        self.horizontalMotionBlur50RadioButton.setText("50% Blur")
        self.horizontalMotionBlur50RadioButton.clicked.connect(self.showHorizontalMotionBlurPreview)
        self.horizontalMotionBlur50RadioButton.show()

        self.horizontalMotionBlur100RadioButton=QRadioButton(self.horizontalMotionBlurDialog)
        self.horizontalMotionBlur100RadioButton.setGeometry(55+80+55+55+80+35,205,80,80)
        self.horizontalMotionBlur100RadioButton.setText("100% Blur")
        self.horizontalMotionBlur100RadioButton.clicked.connect(self.showHorizontalMotionBlurPreview)
        self.horizontalMotionBlur100RadioButton.show()

        self.okButton=QPushButton("Apply",self.horizontalMotionBlurDialog)
        self.okButton.move(140,280)
        self.okButton.clicked.connect(self.applyHorizontalMotionBlur)

        self.cancelButton=QPushButton("Cancel",self.horizontalMotionBlurDialog)
        self.cancelButton.move(220,280)
        self.cancelButton.clicked.connect(self.horizontalMotionBlurDialog.close)

        self.horizontalMotionBlurDialog.exec_()


    def createVerticalMotionBlurWindow(self):
        #open window for guassian blur setup
        self.verticalMotionBlurDialog=QDialog(self)
        self.verticalMotionBlurDialog.resize(450,320)
        self.verticalMotionBlurDialog.setWindowTitle("Set Motion Blur (%) - Vertically")

        self.verticalMotionBlurPreview=QLabel(self.verticalMotionBlurDialog)
        self.verticalMotionBlurPreview.setPixmap(QPixmap("img/previews/carVerticalMotion10.jpg"))
        self.verticalMotionBlurPreview.setGeometry(15,5,420,200)        
        self.verticalMotionBlurPreview.setStyleSheet("border:1px solid black;")
        
        self.verticalMotionBlur10RadioButton=QRadioButton(self.verticalMotionBlurDialog)
        self.verticalMotionBlur10RadioButton.setGeometry(55,205,80,80)
        self.verticalMotionBlur10RadioButton.setText("10% Blur")
        self.verticalMotionBlur10RadioButton.setChecked(True)
        self.verticalMotionBlur10RadioButton.clicked.connect(self.showVerticalMotionBlurPreview)
        self.verticalMotionBlur10RadioButton.show()

        self.verticalMotionBlur20RadioButton=QRadioButton(self.verticalMotionBlurDialog)
        self.verticalMotionBlur20RadioButton.setGeometry(55+80+20,205,80,80)
        self.verticalMotionBlur20RadioButton.setText("20% Blur")
        self.verticalMotionBlur20RadioButton.clicked.connect(self.showVerticalMotionBlurPreview)
        self.verticalMotionBlur20RadioButton.show()

        self.verticalMotionBlur50RadioButton=QRadioButton(self.verticalMotionBlurDialog)
        self.verticalMotionBlur50RadioButton.setGeometry(55+80+55+55+15,205,80,80)
        self.verticalMotionBlur50RadioButton.setText("50% Blur")
        self.verticalMotionBlur50RadioButton.clicked.connect(self.showVerticalMotionBlurPreview)
        self.verticalMotionBlur50RadioButton.show()

        self.verticalMotionBlur100RadioButton=QRadioButton(self.verticalMotionBlurDialog)
        self.verticalMotionBlur100RadioButton.setGeometry(55+80+55+55+80+35,205,80,80)
        self.verticalMotionBlur100RadioButton.setText("100% Blur")
        self.verticalMotionBlur100RadioButton.clicked.connect(self.showVerticalMotionBlurPreview)
        self.verticalMotionBlur100RadioButton.show()

        self.okButton=QPushButton("Apply",self.verticalMotionBlurDialog)
        self.okButton.move(140,280)
        self.okButton.clicked.connect(self.applyVerticalMotionBlur)

        self.okButton=QPushButton("Cancel",self.verticalMotionBlurDialog)
        self.okButton.move(220,280)
        self.okButton.clicked.connect(self.verticalMotionBlurDialog.close)

        self.verticalMotionBlurDialog.exec_()


    def createGuassianBlurWindow(self):
        #open window for guassian blur setup
        self.guassianBlurDialog=QDialog(self)
        self.guassianBlurDialog.resize(450,320)
        self.guassianBlurDialog.setWindowTitle("Set Guassian Blur Percentage (%)")

        self.gaussianBlurPreview=QLabel(self.guassianBlurDialog)
        self.gaussianBlurPreview.setPixmap(QPixmap("img/previews/gaussian20.jpg"))
        self.gaussianBlurPreview.setGeometry(15,5,420,200)        
        self.gaussianBlurPreview.setStyleSheet("border:1px solid black;")
        
        self.gaussian20RadioButton=QRadioButton(self.guassianBlurDialog)
        self.gaussian20RadioButton.setGeometry(55,205,80,80)
        self.gaussian20RadioButton.setText("20% Blur")
        self.gaussian20RadioButton.setChecked(True)
        self.gaussian20RadioButton.clicked.connect(self.showGaussianPreview)
        self.gaussian20RadioButton.show()

        self.gaussian40RadioButton=QRadioButton(self.guassianBlurDialog)
        self.gaussian40RadioButton.setGeometry(55+35+80,205,80,80)
        self.gaussian40RadioButton.setText("40% Blur")
        self.gaussian40RadioButton.clicked.connect(self.showGaussianPreview)
        self.gaussian40RadioButton.show()

        self.gaussian60RadioButton=QRadioButton(self.guassianBlurDialog)
        self.gaussian60RadioButton.setGeometry(55+35+80+35+80,205,80,80)
        self.gaussian60RadioButton.setText("60% Blur")
        self.gaussian60RadioButton.clicked.connect(self.showGaussianPreview)
        self.gaussian60RadioButton.show()

        self.okButton=QPushButton("Apply",self.guassianBlurDialog)
        self.okButton.move(140,280)
        self.okButton.clicked.connect(self.applyGuassianBlur)

        self.okButton=QPushButton("Cancel",self.guassianBlurDialog)
        self.okButton.move(220,280)
        self.okButton.clicked.connect(self.guassianBlurDialog.close)

        self.guassianBlurDialog.exec_()

    
    def createContrastWindow(self):
        #open window for contrast setup
        self.contrastDialog=QDialog(self)
        self.contrastDialog.resize(300,150)
        self.contrastDialog.setWindowTitle("Set Contrast")

        label=QLabel(self.contrastDialog)
        label.setText("Contrast: ")
        label.setGeometry(60,16,100,30)

        self.contrastSlider=QSlider(Qt.Horizontal,self.contrastDialog)
        self.contrastSlider.setFocusPolicy(Qt.NoFocus)
        self.contrastSlider.setTickPosition(QSlider.TicksAbove)
        self.contrastSlider.setTickInterval(10)
        self.contrastSlider.setSingleStep(10)
        self.contrastSlider.setValue(50)
        self.contrastSlider.setGeometry(60,51,170,50)
        self.contrastSlider.valueChanged.connect(self.setContrastFactor)

        self.contrastButton=QPushButton("OK",self.contrastDialog)
        self.contrastButton.move(110,111)
        self.contrastButton.clicked.connect(self.setContrast)

        self.contrastDialog.exec_()
    
    def openOverlayImageChooser(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filePath, _ = QFileDialog.getOpenFileName(self,"Choose an image", "","JPG (*.jpg);;PNG (*.png);;JPEG (*.jpeg);", options=options)
        fileName=""
        if filePath:
            self.overlayImageFilePath=filePath
            fileName=filePath[filePath.rfind("/")+1:]
            #hide the choose button
            self.overlayPanelImageButton.hide()
            self.overlayPanelImageLabel.setText(fileName)
            self.overlayPanelImageLabel.show()
            

    def openFileChooser(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filePath, _ = QFileDialog.getOpenFileName(self,"Choose an image", "","JPG (*.jpg);;PNG (*.png);;JPEG (*.jpeg);", options=options)
        if filePath:

            temp=cv2.imread(filePath)
            height,width,depth=temp.shape
            extension=""
            if filePath.endswith(".jpg"): extension="jpg"
            else: extension="png"

            cv2.imwrite("originalImage."+extension,temp)

            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            fileName=filePath[filePath.rfind("/")+1:]

            self.images["undoStack"]=list()
            self.images["redoStack"]=list()

            self.images["undoStack"].append("originalImage."+extension)
            
            self.images["path"]="originalImage."+extension
            self.images["name"]=fileName
            self.images["filterImageName"]=""
            self.images["height"]=height
            self.images["width"]=width
            self.images["extension"]=extension
            self.images["size"]=fileSize
            self.images["status"]="File opened..."
            self.update()
            self.createPanels()
            self.updateStatusBar()
            

    def saveFileChooser(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"Save","","JPEG (*.jpeg);;PNG (*.png)", options=options)
        if fileName:
            self.saveResult(fileName)
    
    def saveResult(self,saveWith):
        imagePath=self.images["filterImageName"]
        if imagePath=="":
            imagePath=self.images["path"]
        if imagePath.endswith(".png"):
            saveWith+=".png"
        else:
            saveWith+=".jpg"
        contents=cv2.imread(imagePath)
        cv2.imwrite(saveWith,contents)
        self.images["status"]="file saved successfully..."
        self.updateStatusBar()
    
    class ImageProcessor:
        def __init__(self,TMApplication):
            self.tmApplication=TMApplication
        
        def performReplicateBorderOperation(self,borderDetails):
            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]

            imageData=cv2.imread(filePath)
            thickness=borderDetails["thickness"]
            borderType=borderDetails["border-type"]

            if borderType=="replicate_standard":
                outputImageData=cv2.copyMakeBorder(imageData, thickness, thickness, thickness, thickness, cv2.BORDER_REFLECT) 
            else:
                top=thickness[0]
                bottom=thickness[1]
                left=thickness[2]
                right=thickness[3]
                outputImageData=cv2.copyMakeBorder(imageData, top, bottom, left, right, cv2.BORDER_REFLECT) 

            if filePath.endswith(".png"):
                filePath="border-replicate.png"
            else:
                filePath="border-replicate.jpg"

            cv2.imwrite(filePath,outputImageData)
            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Border applied successfully...."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath      

        def performNormalBorderOperation(self,borderDetails):
            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]

            imageData=cv2.imread(filePath)
            thickness=borderDetails["thickness"]
            color=borderDetails["color"]
            borderType=borderDetails["border-type"]
            color=convertToRGB(color)
            color=list(color)
            color[0],color[2]=color[2],color[0]

            if borderType=="normal_standard":
                outputImageData=cv2.copyMakeBorder(imageData, thickness, thickness, thickness, thickness, cv2.BORDER_CONSTANT,value=color) 
            else:
                top=thickness[0]
                bottom=thickness[1]
                left=thickness[2]
                right=thickness[3]
                outputImageData=cv2.copyMakeBorder(imageData, top, bottom, left, right, cv2.BORDER_CONSTANT,value=color) 

            if filePath.endswith(".png"):
                filePath="border.png"
            else:
                filePath="border.jpg"

            cv2.imwrite(filePath,outputImageData)
            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Border applied successfully...."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath      
            
        
        def performTextWatermark(self,text,textSize,textThickness,opacity,coordinates):
            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]
            
            imageData = cv2.imread(filePath)
            overlay = imageData.copy()
            outputImageData = imageData.copy()
            height, width = imageData.shape[:2]

            alpha = opacity/100
            cv2.putText(overlay, text.format(alpha), coordinates, cv2.FONT_HERSHEY_PLAIN, textSize, (0,0,0), thickness=textThickness)
            cv2.addWeighted(overlay, alpha, outputImageData, 1 - alpha, 0, outputImageData)

            if filePath.endswith(".png"):
                filePath="watermark-text.png"
            else:
                filePath="watermark-text.jpg"

            cv2.imwrite(filePath,outputImageData)
            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Watermark applied successfully...."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath      
        
        def performImageWatermark(self,sourceImage,opacity,coordinates):
            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]
            scale=1
            imageData=cv2.imread(filePath,-1)  
            outputImageData=imageData.copy()          
            opacity=opacity/100
            watermarkImageData=cv2.imread(sourceImage,-1)
            watermarkImageData = cv2.resize(watermarkImageData, (0, 0), fx=scale, fy=scale)
            height,width,depth=watermarkImageData.shape
            rows,columns,_=imageData.shape
            y,x=coordinates[0],coordinates[1]
            for i in range(height):
                for j in range(width):
                    if x + i >= rows or y + j >= columns:
                        continue
                    alpha = float(watermarkImageData[i][j][3] / 255.0)  # read the alpha channel
                    imageData[x + i][y + j] = alpha * watermarkImageData[i][j][:3] + (1 - alpha) * imageData[x + i][y + j]
            
            cv2.addWeighted(imageData,opacity,outputImageData,1-opacity,0,outputImageData)

            if filePath.endswith(".png"):
                filePath="watermark-image.png"
            else:
                filePath="watermark-image.jpg"

            cv2.imwrite(filePath,outputImageData)
            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Watermark applied successfully...."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath  

        def performZoomOut(self):
            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]
            imageData=cv2.imread(filePath)
            height,width,depth=imageData.shape
            try:
                outputImageData=cv2.resize(imageData, None, fx= 0.5, fy= 0.5, interpolation= cv2.INTER_LINEAR)
            except:
                print("Failed to perform operation. Invalid Input !")
            
            if filePath.endswith(".png"):
                filePath="zoom-out.png"
            else:
                filePath="zoom-out.jpg"
            
            cv2.imwrite(filePath,outputImageData)
            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
            self.tmApplication.images["height"]=outputImageData.shape[0]
            self.tmApplication.images["width"]=outputImageData.shape[1]
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Zoomed-out Successfully...."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath  
        
        def performZoomIn(self):
            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]
            imageData=cv2.imread(filePath)
            outputImageData=cv2.resize(imageData, None, fx= 1.5, fy= 1.2, interpolation= cv2.INTER_LINEAR)
            
            if filePath.endswith(".png"):
                filePath="zoom-in.png"
            else:
                filePath="zoom-in.png"
            
            cv2.imwrite(filePath,outputImageData)
            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
            self.tmApplication.images["height"]=outputImageData.shape[0]
            self.tmApplication.images["width"]=outputImageData.shape[1]
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Zoomed-in Successfully...."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath  

        def performTextOperation(self,text,fontPath,fontColor,fontSize,x,y):
            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]
            imageData=Image.open(filePath)
            draw = ImageDraw.Draw(imageData)  
            font = ImageFont.truetype(fontPath, int(fontSize))             
            fontColor="rgb"+str(convertToRGB(fontColor))
            coordinates=list()
            coordinates.append(x)
            coordinates.append(y)
            coordinates=tuple(coordinates)
            draw.text(coordinates, text, fill=fontColor, font = font) 

            if filePath.endswith(".png"):
                imageData.save("text.png")
                filePath="text.png"
            else:
                imageData.save("text.jpg")
                filePath="text.jpg"
            
            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Text Applied Successfully...."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath  
        
        def performLaplace(self):
            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]
            imageData=cv2.imread(filePath)
            height,width,depth=imageData.shape

            grayData=cv2.cvtColor(imageData, cv2.COLOR_BGR2GRAY) 
            laplaceData=grayData
            verticalFilter=[
                [1,2,1],
                [0,0,0],
                [-1,-2,-1]
            ]

            horizontalFilter=[
                [1,0,-1],
                [2,0,-2],
                [1,0,-1]
            ]

            height=height-3+1
            width=width-3+1

            for i in range(height):
                for j in range(width):
                    sumX=0
                    sumY=0
                    for k in range(3):
                        for l in range(3):
                            sumX+=(verticalFilter[k][l]*grayData[i+k][j+l])
                            sumY+=(horizontalFilter[k][l]*grayData[i+k][j+l])
                
                    laplaceData[i][j]=math.sqrt(pow(sumX,2)+pow(sumY,2))/math.sqrt(pow(1.9,2)+pow(1.9,2))


            if filePath.endswith(".png"):
                cv2.imwrite("laplace.png",laplaceData)
                filePath="laplace.png"
            else:
                cv2.imwrite("laplace.jpg",laplaceData)
                filePath="laplace.jpg"
            
            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Converted to Laplace...."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath  
        
        def performUnsharpening(self):
            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]
            imageData=cv2.imread(filePath)
            height,width,depth=imageData.shape

            kernel = [[1 / 9, 1 / 9, 1 / 9],
                    [1 / 9, 1 / 9, 1 / 9],
                    [1 / 9, 1 / 9, 1 / 9]]

            amount = 2
            offset = len(kernel) // 2

            outputImageData = np.zeros((height,width,depth))

            # Compute convolution with kernel
            for x in range(offset, height - offset):
                for y in range(offset, width - offset):
                    original_pixel = imageData[x][y]
                    acc = [0, 0, 0]
                    for a in range(len(kernel)):
                        for b in range(len(kernel)):
                            xn = x + a - offset
                            yn = y + b - offset
                            pixel = imageData[xn][yn]
                            acc[0] += pixel[0] * kernel[a][b]
                            acc[1] += pixel[1] * kernel[a][b]
                            acc[2] += pixel[2] * kernel[a][b]

                    new_pixel = (
                        int(original_pixel[0] + (original_pixel[0] - acc[0]) * amount),
                        int(original_pixel[1] + (original_pixel[1] - acc[1]) * amount),
                        int(original_pixel[2] + (original_pixel[2] - acc[2]) * amount)
                    )
                    outputImageData[x][y]=new_pixel
            
            if filePath.endswith(".png"):
                cv2.imwrite("unsharp.png",outputImageData)
                filePath="unsharp.png"
            else:
                cv2.imwrite("unsharp.jpg",outputImageData)
                filePath="unsharp.jpg"
            
            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Unsharpening Done...."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath  
        
        def performSharpening(self):
            kernel = [[  0  , -.5 ,    0 ],
            [-.5 ,   3  , -.5 ],
            [  0  , -.5 ,    0 ]]

            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]
            imageData=cv2.imread(filePath)
            height,width,depth=imageData.shape

            offset = len(kernel) // 2
            outputImageData = np.zeros(imageData.shape)

            for x in range(offset, height - offset):
                for y in range(offset, width - offset):
                    acc = [0, 0, 0]
                    for a in range(len(kernel)):
                        for b in range(len(kernel)):
                            xn = x + a - offset
                            yn = y + b - offset
                            pixel = imageData[xn][yn]
                            acc[0] += pixel[0] * kernel[a][b]
                            acc[1] += pixel[1] * kernel[a][b]
                            acc[2] += pixel[2] * kernel[a][b]

                    outputImageData[x][y][0]=acc[0]
                    outputImageData[x][y][1]=acc[1]
                    outputImageData[x][y][2]=acc[2]

            if filePath.endswith(".png"):
                cv2.imwrite("sharpen.png",outputImageData)
                filePath="sharpen.png"
            else:
                cv2.imwrite("sharpen.jpg",outputImageData)
                filePath="sharpen.jpg"
            
            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Sharpening Done...."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath  

        def performInvert(self):
            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]
            imageData=cv2.imread(filePath)
            height,width,depth=imageData.shape
            outputImageData=imageData
            for i in range(height):
                for j in range(width):
                    blue=outputImageData[i][j][0]
                    green=outputImageData[i][j][1]
                    red=outputImageData[i][j][2]

                    outputImageData[i][j][0]=255-blue
                    outputImageData[i][j][1]=255-green
                    outputImageData[i][j][2]=255-red

            if filePath.endswith(".png"):
                cv2.imwrite("invert.png",outputImageData)
                filePath="invert.png"
            else:
                cv2.imwrite("invert.jpg",outputImageData)
                filePath="invert.jpg"
            
            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Inverted...."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath  
        
        def performBoxBlur(self):
            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]
            imageData=cv2.imread(filePath)
            height,width,depth=imageData.shape

            boxKernel=[
            [1/9,1/9,1/9],
            [1/9,1/9,1/9],
            [1/9,1/9,1/9]
            ]

            offset=len(boxKernel)//2
            outputImage=np.zeros((height,width,depth))

            for i in range(1):
                for x in range(offset,height-offset):
                    for y in range(offset,width-offset):
                        red=0
                        green=0
                        blue=0
                        for a in range(len(boxKernel)):
                            for b in range(len(boxKernel)):
                                xn=x+a-offset
                                yn=y+b-offset
                                pixels=imageData[xn][yn]
                                blue+=pixels[0]*boxKernel[a][b]
                                green+=pixels[1]*boxKernel[a][b]
                                red+=pixels[2]*boxKernel[a][b]
                        outputImage[x][y][0]=blue
                        outputImage[x][y][1]=green
                        outputImage[x][y][2]=red

            if filePath.endswith(".png"):
                cv2.imwrite("boxBlur.png",outputImage)
                filePath="boxBlur.png"
            else:
                cv2.imwrite("boxBlur.jpg",outputImage)
                filePath="boxBlur.jpg"
            
            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Box Blur applied successfully...."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath  

        def convolution(self,oldimage, kernel):
            #image = Image.fromarray(image, 'RGB')
            image_h = oldimage.shape[0]
            image_w = oldimage.shape[1]
            
            
            kernel_h = kernel.shape[0]
            kernel_w = kernel.shape[1]
            
            if(len(oldimage.shape) == 3):
                image_pad = np.pad(oldimage, pad_width=((kernel_h // 2, kernel_h // 2),(kernel_w // 2, kernel_w // 2),(0,0)), mode='constant', constant_values=0).astype(np.float32)    
            elif(len(oldimage.shape) == 2):
                image_pad = np.pad(oldimage, pad_width=((kernel_h // 2, kernel_h // 2),(kernel_w // 2, kernel_w // 2)), mode='constant', constant_values=0).astype(np.float32)
                    
            h = kernel_h // 2
            w = kernel_w // 2
            
            image_conv = np.zeros(image_pad.shape)
            
            for i in range(h, image_pad.shape[0]-h):
                for j in range(w, image_pad.shape[1]-w):
                    #sum = 0
                    x = image_pad[i-h:i-h+kernel_h, j-w:j-w+kernel_w]
                    x = x.flatten()*kernel.flatten()
                    image_conv[i][j] = x.sum()
            h_end = -h
            w_end = -w
            
            if(h == 0):
                return image_conv[h:,w:w_end]
            if(w == 0):
                return image_conv[h:h_end,w:]    
            return image_conv[h:h_end,w:w_end]
        
        def performHorizontalMotionBlur(self,kernelSize):
            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]
            image=cv2.imread(filePath)  
            horizontalKernel=np.zeros((kernelSize,kernelSize))
            horizontalKernel[int((kernelSize-1)/2),:]=np.ones(kernelSize)
            for i in range(kernelSize):
                for j in range(kernelSize):
                    horizontalKernel[i][j]/=kernelSize
            im_filtered = np.zeros_like(image)
            for c in range(3):
                im_filtered[:, :, c] = self.convolution(image[:, :, c], horizontalKernel) 
            blurData=(im_filtered.astype(np.uint8))

            if filePath.endswith(".png"):
                cv2.imwrite("horizontalMotion-blur.png",blurData)
                filePath="horizontalMotion-blur.png"
            else:
                cv2.imwrite("horizontalMotion-blur.jpg",blurData)
                filePath="horizontalMotion-blur.jpg"
            
            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Horizontal Motion Blur applied successfully...."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath  
        
        def performVerticalMotionBlur(self,kernelSize):
            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]
            image=cv2.imread(filePath)

            verticalKernel=np.zeros((kernelSize,kernelSize))
            verticalKernel[:,int((kernelSize-1)/2)]=np.ones(kernelSize)
            for i in range(kernelSize):
                for j in range(kernelSize):
                    verticalKernel[i][j]/=kernelSize
            im_filtered = np.zeros_like(image)
            for c in range(3):
                im_filtered[:, :, c] = self.convolution(image[:, :, c], verticalKernel)    
            blurData=(im_filtered.astype(np.uint8))

            if filePath.endswith(".png"):
                cv2.imwrite("verticalMotion-blur.png",blurData)
                filePath="verticalMotion-blur.png"
            else:
                cv2.imwrite("verticalMotion-blur.jpg",blurData)
                filePath="verticalMotion-blur.jpg"
            
            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Vertical Motion Blur applied successfully...."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath
        
        def performGuassianBlur(self,radius):
            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]
            image=cv2.imread(filePath)

            filter_size = 2 * int(4 * radius + 0.5) + 1
            gaussian_filter = np.zeros((filter_size, filter_size))
            m = filter_size//2
            n = filter_size//2
            
            for x in range(-m, m+1):
                for y in range(-n, n+1):
                    x1 = 2*np.pi*(radius**2)
                    x2 = np.exp(-(x**2 + y**2)/(2* radius**2))
                    gaussian_filter[x+m, y+n] = (1/x1)*x2
            
            im_filtered = np.zeros_like(image)
            for c in range(3):
                im_filtered[:, :, c] = self.convolution(image[:, :, c], gaussian_filter)    
            blurData=im_filtered.astype(np.uint8)
            
            if filePath.endswith(".png"):
                cv2.imwrite("guassian-blur.png",blurData)
                filePath="guassian-blur.png"
            else:
                cv2.imwrite("guassian-blur.jpg",blurData)
                filePath="guassian-blur.jpg"
            
            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Blur applied successfully...."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath
        
        def performResize(self,destHeight,destWidth):
            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]
            sourceImage=cv2.imread(filePath)
            sourceHeight=sourceImage.shape[0]
            sourceWidth=sourceImage.shape[1]

            destImage=numpy.zeros((destHeight,destWidth,3))

            srcY=(sourceHeight/destHeight)
            srcX=(sourceWidth/destWidth)

            for i in range(destHeight):  
                for j in range(destWidth):
                    dstX=math.ceil(j*srcX)
                    dstY=math.ceil(i*srcY) 
                    if dstX==sourceWidth or dstY==sourceHeight: break
                    destImage[i][j]=sourceImage[dstY][dstX]
            
            if filePath.endswith(".png"):
                cv2.imwrite("resize.png",destImage)
                filePath="resize.png"
            else:
                cv2.imwrite("resize.jpg",destImage)
                filePath="resize.jpg"
            
            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
            self.tmApplication.images["height"]=destHeight
            self.tmApplication.images["width"]=destWidth
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Resized successfully...."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath
        
        def performOverlay(self,startingX,startingY):
            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]
            imageOne=cv2.imread(filePath)
            imageTwo=cv2.imread(self.tmApplication.overlayImageFilePath)

            height=imageTwo.shape[0]
            width=imageTwo.shape[1]

            r=int(startingX)
            rr=0
            while rr<height and r<imageOne.shape[0]:
                c=int(startingY)
                cc=0
                while cc<width and c<imageOne.shape[1]:
                    imageOne[r][c]=imageTwo[rr][cc]
                    c+=1
                    cc+=1
                r+=1
                rr+=1
            
            if filePath.endswith(".png"):
                cv2.imwrite("overlay.png",imageOne)
                filePath="overlay.png"
            else:
                cv2.imwrite("overlay.jpg",imageOne)
                filePath="overlay.jpg"

            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
    
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Overlay done successfully...."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath

        def performClockwise(self):
            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]
            imageData=cv2.imread(filePath)
            height=imageData.shape[0]
            width=imageData.shape[1]
            newImageData=numpy.zeros((width,height,3))

            r=0
            rr=height-1
            while r<height:
                c=0
                cc=0
                while c<width:
                    newImageData[cc][rr]=imageData[r][c]
                    c+=1
                    cc+=1
                r+=1
                rr-=1

            if filePath.endswith(".png"):
                cv2.imwrite("cw-90.png",newImageData)
                filePath="cw-90.png"
            else:
                cv2.imwrite("cw-90.jpg",newImageData)
                filePath="cw-90.jpg"
            
            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
            self.tmApplication.images["height"]=width
            self.tmApplication.images["width"]=height
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Rotated successfully...."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath


        def performAnticlockwise(self):
            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]
            imageData=cv2.imread(filePath)
            height=imageData.shape[0]
            width=imageData.shape[1]

            newImageData=numpy.zeros((width,height,3))

            r=0
            rr=0
            while r<height:
                c=width-1
                cc=0
                while c>0:
                    newImageData[cc][rr]=imageData[r][c]
                    c-=1
                    cc+=1
                r+=1
                rr+=1

            if filePath.endswith(".png"):
                cv2.imwrite("acw-90.png",newImageData)
                filePath="acw-90.png"
            else:
                cv2.imwrite("acw-90.jpg",newImageData)
                filePath="acw-90.jpg"
                
            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
            self.tmApplication.images["height"]=width
            self.tmApplication.images["width"]=height
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Rotated successfully..."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath

        def perform180(self):
            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]
            imageData=cv2.imread(filePath)
            height=imageData.shape[0]
            width=imageData.shape[1]

            newImageData=numpy.zeros((height,width,3))

            r=0
            rr=height-1
            while r<height:
                c=0
                cc=width-1
                while c<width:
                    newImageData[rr][cc]=imageData[r][c]
                    c+=1
                    cc-=1
                r+=1
                rr-=1

            if filePath.endswith(".png"):
                cv2.imwrite("rotate-180.png",newImageData)
                filePath="rotate-180.png"
            else:
                cv2.imwrite("rotate-180.jpg",newImageData)
                filePath="rotate-180.jpg"
                
            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
            self.tmApplication.images["height"]=height
            self.tmApplication.images["width"]=width
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Rotated successfully..."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath

        
        def performHorizontalFlip(self):
            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]
            imageData=cv2.imread(filePath)
            height=imageData.shape[0]
            width=imageData.shape[1]

            newImageData=numpy.zeros((height,width,3))

            r=0
            rr=0
            while r<height:
                c=0
                cc=width-1
                while c<width:
                    newImageData[rr][cc]=imageData[r][c]
                    c+=1
                    cc-=1
                r+=1
                rr+=1

            if filePath.endswith(".png"):
                cv2.imwrite("flip-vertical.png",newImageData)
                filePath="flip-vertical.png"
            else:
                cv2.imwrite("flip-vertical.jpg",newImageData)
                filePath="flip-vertical.jpg"
                
            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Flipped Horizontally..."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath

        def performVerticalFlip(self):
            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]
            imageData=cv2.imread(filePath)
            height=imageData.shape[0]
            width=imageData.shape[1]

            newImageData=numpy.zeros((height,width,3))

            r=0
            rr=height-1
            while r<height:
                c=0
                cc=0
                while c<width:
                    newImageData[rr][cc]=imageData[r][c]
                    c+=1
                    cc+=1
                r+=1
                rr-=1

            if filePath.endswith(".png"):
                cv2.imwrite("flip-vertical.png",newImageData)
                filePath="flip-vertical.png"
            else:
                cv2.imwrite("flip-vertical.jpg",newImageData)
                filePath="flip-vertical.jpg"
                
            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Flipped Vertically..."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath
        
        def performCrop(self,startingX,startingY,endingX,endingY):
            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]
            imageData=cv2.imread(filePath)
            cropSize=(endingX,endingY)
            c1=int(startingX)
            r1=int(startingY)
            c2=int(endingY)
            r2=int(endingX)
            if r2>=imageData.shape[0]: r2=imageData.shape[0]-1
            if c2>=imageData.shape[1]: c2=imageData.shape[1]-1
            cropSize=(c2-c1+1,r2-r1+1)
            newImage=numpy.zeros((cropSize[1],cropSize[0],3))
            rr=0
            r=r1
            while r<=r2:
                cc=0
                c=c1
                while c<=c2:
                    newImage[rr][cc]=imageData[r][c]
                    c+=1
                    cc+=1
                r+=1
                rr+=1

            if filePath.endswith(".png"):
                cv2.imwrite("crop.png",newImage)
                filePath="crop.png"
            else:
                cv2.imwrite("crop.jpg",newImage)
                filePath="crop.jpg"
        
            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
            self.tmApplication.images["height"]=endingY
            self.tmApplication.images["width"]=endingX
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Cropped Successfully..."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath

        def getPreviewForCrop(self,startingX,startingY,endingX,endingY):
            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]
            imageData=cv2.imread(filePath)
            cropSize=(endingX,endingY)
            c1=int(startingX)
            r1=int(startingY)
            c2=int(endingY)
            r2=int(endingX)
            if r2>=imageData.shape[0]: r2=imageData.shape[0]-1
            if c2>=imageData.shape[1]: c2=imageData.shape[1]-1
            cropSize=(c2-c1+1,r2-r1+1)

            r=r1
            while r<=r2:
                imageData[r][c1]=(0,0,255)
                imageData[r][c2]=(0,0,255)
                r+=1
            c=c1
            while c<=c2:
                imageData[r1][c]=(0,0,255)
                imageData[r2][c]=(0,0,255)
                c+=1
            if filePath.endswith(".png"):
                cv2.imwrite("preview.png",imageData)
                filePath="preview.png"
            else:
                cv2.imwrite("preview.jpg",imageData)
                filePath="preview.jpg"

            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Showing Preview..."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath


        def performContrastOperation(self,contrastFactor):
            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]
            imageData=cv2.imread(filePath)
            height,width,depth=imageData.shape
            grayData=np.zeros((height,width,depth))
            f=(259* (contrastFactor+255))/(255* (259-contrastFactor))
            howMuch=(255/100)*contrastFactor
            for i in range(height):
                for j in range(width):
                    rgb=imageData[i][j]
                    red=rgb[0]
                    green=rgb[1]
                    blue=rgb[2]
                    newRed=(f*(red-128))+128
                    newGreen=(f*(green-128))+128
                    newBlue=(f*(blue-128))+128
                    if contrastFactor<50: 
                        newRed-=howMuch
                        newGreen-=howMuch
                        newBlue-=howMuch
                    else:
                        newRed+=howMuch
                        newGreen+=howMuch
                        newBlue+=howMuch
                    if newRed>255: newRed=255
                    if newRed<0: newRed=0
                    if newGreen>255: newGreen=255
                    if newGreen<0: newGreen=0
                    if newBlue>255: newBlue=255
                    if newBlue<0: newBlue=0
                    grayData[i][j]=(newRed,newGreen,newBlue)

            if filePath.endswith(".png"):
                cv2.imwrite("contrast.png",grayData)
                filePath="contrast.png"
            else:
                cv2.imwrite("contrast.jpg",grayData)
                filePath="contrast.jpg"
                
            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Done..."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath

        def performBrightnessOperation(self,value):
            filePath=self.tmApplication.images["filterImageName"]
            if filePath=="": filePath=self.tmApplication.images["path"]
            imageData=cv2.imread(filePath)
            height,width,depth=imageData.shape
            grayData=np.zeros((height,width,depth))
            brightnessFactor=100-value
            x=int((255/100)*brightnessFactor)           
            for i in range(height):
                for j in range(width):
                    rgb=imageData[i][j]
                    red=rgb[0]
                    green=rgb[1]
                    blue=rgb[2]
                    if brightnessFactor<50: 
                        red+=x
                        green+=x
                        blue+=x
                    else:
                        red-=x
                        green-=x
                        blue-=x
                    if red>255: red=255
                    if red<0: red=0
                    if green>255: green=255
                    if green<0: green=0
                    if blue>255: blue=255
                    if blue<0: blue=0
                    grayData[i][j]=(red,green,blue)

            if filePath.endswith(".png"):
                cv2.imwrite("brightness.png",grayData)
                filePath="brightness.png"
            else:
                cv2.imwrite("brightness.jpg",grayData)
                filePath="brightness.jpg"

            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"

            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Done..."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath

        def performGrayScale(self):
            filePath=self.tmApplication.images["path"]
            imageData=cv2.imread(filePath)
            height,width,depth=imageData.shape
            grayData=np.zeros((height,width,depth))

            for i in range(height):
                for j in range(width):
                    avg=int(int(imageData[i][j][0]) + int(imageData[i][j][1]) + int(imageData[i][j][2])) / 3
                    grayData[i][j][0]=avg
                    grayData[i][j][1]=avg
                    grayData[i][j][2]=avg
            
            if filePath.endswith(".png"):
                cv2.imwrite("grayScale.png",grayData)
                filePath="grayScale.png"
            else:
                cv2.imwrite("grayScale.jpg",grayData)
                filePath="grayScale.jpg"

            fileSize=os.stat(filePath)
            fileSize=((fileSize.st_size)/(1024*1024))
            fileSize=round(fileSize,3)
            if filePath.endswith(".jpg"): self.tmApplication.images["extension"]="jpg"
            else: self.tmApplication.images["extension"]="png"
            self.tmApplication.images["size"]=fileSize
            self.tmApplication.images["status"]="Converted to Gray Scale successfully..."
            self.tmApplication.images["undoStack"].append(filePath)
            self.tmApplication.images["filterImageName"]=filePath


if __name__=="__main__":
    app=QApplication(sys.argv)
    model=DataModel(1250,700)
    window=TMApplication(model)
    splash=QSplashScreen()
    splash.setPixmap(QPixmap("img/splash-bg.png"))
    splash.show()
    statusLabel=QLabel(splash)
    statusLabel.setGeometry(483,260,110,20)
    statusLabel.show()
    progressBar=QProgressBar(splash)
    progressBar.setGeometry(3,283,592,15)
    progressBar.setStyleSheet("QProgressBar::chunk{background-color:#9da603;}")
    progressBar.setAlignment(QtCore.Qt.AlignCenter) 
    progressBar.setFormat("Loading...")
    progressBar.show()
    j=0
    logsSize=len(window.logFiles)
    for i in range(101):
        progressBar.setValue(i)
        if j<logsSize:
            time.sleep(0.5) 
            statusLabel.setText(window.logFiles[i])
            j+=1
        t=time.time()
        while time.time()<t+0.1:
            app.processEvents()
    splash.close()
    window.show()
    sys.exit(app.exec_())
