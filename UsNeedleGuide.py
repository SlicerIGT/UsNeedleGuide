import os
from __main__ import vtk, qt, ctk, slicer

from Guidelet import GuideletLoadable, GuideletLogic, GuideletTest, GuideletWidget
from Guidelet import Guidelet
import logging
import time
import numpy as np


class UsNeedleGuide(GuideletLoadable):
  """Uses GuideletLoadable class, available at:
  """

  def __init__(self, parent):
    GuideletLoadable.__init__(self, parent)
    self.parent.title = "Ultrasound needle guide"
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["YOUR NAME"]
    self.parent.helpText = """ SOME HELP AND A LINK TO YOUR WEBSITE """
    self.parent.acknowledgementText = """ THANKS TO ... """


class UsNeedleGuideWidget(GuideletWidget):
  """Uses GuideletWidget base class, available at:
  """

  def __init__(self, parent = None):
    GuideletWidget.__init__(self, parent)


  def setup(self):
    GuideletWidget.setup(self)
    self.guideletLogic = self.createGuideletLogic()

  def addLauncherWidgets(self):
    GuideletWidget.addLauncherWidgets(self)


  def onConfigurationChanged(self, selectedConfigurationName):
    GuideletWidget.onConfigurationChanged(self, selectedConfigurationName)
    #settings = slicer.app.userSettings()


  def addBreachWarningLightPreferences(self):
    pass


  def onBreachWarningLightChanged(self, state):
    pass


  def createGuideletInstance(self):
    return UsNeedleGuideGuidelet(None, self.guideletLogic, self.selectedConfigurationName)


  def createGuideletLogic(self):
    return UsNeedleGuideLogic()


class UsNeedleGuideLogic(GuideletLogic):
  """Uses GuideletLogic base class, available at:
  """ #TODO add path


  def __init__(self, parent = None):
    GuideletLogic.__init__(self, parent)


  def addValuesToDefaultConfiguration(self):
    GuideletLogic.addValuesToDefaultConfiguration(self)
    moduleDir = os.path.dirname(slicer.modules.usneedleguide.path)
    defaultSceneSavePath = os.path.join(moduleDir, 'SavedScenes')
    moduleDirectoryPath = slicer.modules.usneedleguide.path.replace('UsNeedleGuide.py','')
    settingList = {
                   'StyleSheet' : moduleDirectoryPath + 'Resources/StyleSheets/UsNeedleGuideStyle.qss',
                   'LiveUltrasoundNodeName': 'Image_Image',
                   'TestMode' : 'False',
                   'RecordingFilenamePrefix' : 'UsNeedleGuideRec-',
                   'SavedScenesDirectory': defaultSceneSavePath, #overwrites the default setting param of base
                   }
    self.updateSettings(settingList, 'Default')
   
class UsNeedleGuideTest(GuideletTest):
  """This is the test case for your scripted module.
  """

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    GuideletTest.runTest(self)
    #self.test_UsNeedleGuide1() #add applet specific tests here


class UsNeedleGuideGuidelet(Guidelet):
  
  GUIDECOLORS = np.array([
    [0.2, 1.0, 0.0],
    [0.2, 0.8, 0.3],
    [0.2, 0.6, 0.6],
    [0.2, 0.4, 1.0]
  ], dtype=object)

  PROBEMODEL_TO_IMAGE_FILENAME = "ProbeModelToImage.h5"
  PROBEMODEL_TO_IMAGE = "ProbeModelToImage"
  
  
  def __init__(self, parent, logic, configurationName='Default'):
    self.calibrationCollapsibleButton = None

    Guidelet.__init__(self, parent, logic, configurationName)
    logging.debug('UsNeedleGuideGuidelet.__init__')

    self.logic.addValuesToDefaultConfiguration()

    moduleDirectoryPath = slicer.modules.usneedleguide.path.replace('UsNeedleGuide.py', '')

    # Set up main frame.

    self.sliceletDockWidget.setObjectName('UsNeedleGuidePanel')
    self.sliceletDockWidget.setWindowTitle('Ultrasound needle guide')
    self.mainWindow.setWindowTitle('UsNeedleGuide')
    self.mainWindow.windowIcon = qt.QIcon(moduleDirectoryPath + '/Resources/Icons/UsNeedleGuide.png')

    self.setupScene()

    self.navigationView = self.VIEW_ULTRASOUND_3D

    # Setting button open on startup.
    
    self.calibrationCollapsibleButton.setProperty('collapsed', True)
    self.ultrasoundCollapsibleButton.setProperty('collapsed', False)
    self.selectView(self.VIEW_ULTRASOUND)


  def createFeaturePanels(self):
    # Create GUI panels.

    self.calibrationCollapsibleButton = ctk.ctkCollapsibleButton()
    self.patientSetupPanel()
    
    featurePanelList = Guidelet.createFeaturePanels(self)

    self.setupUltrasoundPanel()


    featurePanelList[len(featurePanelList):] = [self.calibrationCollapsibleButton]

    return featurePanelList

  
  def setupUltrasoundPanel(self):
  
    self.ultrasoundPresetsLayout = qt.QGridLayout()
    self.ultrasoundPresetsLayout.setContentsMargins(10, 10, 10, 10)
    self.ultrasoundPresetsLayout.setHorizontalSpacing(25)
    self.ultrasoundPresetsLayout.setVerticalSpacing(25)

    self.depthSlider = slicer.qSlicerUltrasoundDoubleParameterSlider()
    self.depthSlider.setParameterName('DepthMm')
    self.depthSlider.setSuffix(' mm')
    self.depthSlider.setMinimum(90.0)
    self.depthSlider.setMaximum(240.0)
    self.depthSlider.setSingleStep(30.0)
    self.depthSlider.setPageStep(30.0)
    self.depthSlider.setConnectorNode(self.connectorNode)
    self.depthSlider.setDeviceID('VideoDevice')
    self.depthSlider.setToolTip("Adjust depth.")

    self.focusSlider = slicer.qSlicerUltrasoundDoubleParameterSlider()
    self.focusSlider.setParameterName('FocusDepthPercent')
    self.focusSlider.setSuffix('%')
    self.focusSlider.setMinimum(0.0)
    self.focusSlider.setMaximum(100.0)
    self.focusSlider.setSingleStep(3)
    self.focusSlider.setPageStep(10)
    self.focusSlider.setConnectorNode(self.connectorNode)
    self.focusSlider.setDeviceID('VideoDevice')
    self.focusSlider.setToolTip("Adjust focus depth.")

    self.dynamicRangeSlider = slicer.qSlicerUltrasoundDoubleParameterSlider()
    self.dynamicRangeSlider.setParameterName('DynRangeDb')
    self.dynamicRangeSlider.setSuffix(' dB')
    self.dynamicRangeSlider.setMinimum(36.0)
    self.dynamicRangeSlider.setMaximum(102.0)
    self.dynamicRangeSlider.setSingleStep(6.0)
    self.dynamicRangeSlider.setPageStep(6.0)
    self.dynamicRangeSlider.setConnectorNode(self.connectorNode)
    self.dynamicRangeSlider.setDeviceID('VideoDevice')
    self.dynamicRangeSlider.setToolTip("Adjust dynamic range.")

    self.frequencySlider = slicer.qSlicerUltrasoundDoubleParameterSlider()
    self.frequencySlider.setParameterName('FrequencyMhz')
    self.frequencySlider.setSuffix(' MHz')
    self.frequencySlider.setMinimum(2.0)
    self.frequencySlider.setMaximum(5.0)
    self.frequencySlider.setSingleStep(0.5)
    self.frequencySlider.setPageStep(1.0)
    self.frequencySlider.setConnectorNode(self.connectorNode)
    self.frequencySlider.setDeviceID('VideoDevice')
    self.frequencySlider.setToolTip("Adjust frequency.")

    self.gainSlider = slicer.qSlicerUltrasoundDoubleParameterSlider()
    self.gainSlider.setParameterName('GainPercent')
    self.gainSlider.setSuffix('%')
    self.gainSlider.setMinimum(0.0)
    self.gainSlider.setMaximum(100.0)
    self.gainSlider.setSingleStep(1.0)
    self.gainSlider.setPageStep(10.0)
    self.gainSlider.setConnectorNode(self.connectorNode)
    self.gainSlider.setDeviceID('VideoDevice')
    self.gainSlider.setToolTip("Adjust gain.")

    depthLabel = qt.QLabel('Depth:')
    depthLabel.setObjectName('presets')
    focusLabel = qt.QLabel('Focus:')
    focusLabel.setObjectName('presets')
    dynamicRangeLabel = qt.QLabel('Dynamic Range:')
    dynamicRangeLabel.setObjectName('presets')
    frequencyLabel = qt.QLabel('Frequency:')
    frequencyLabel.setObjectName('presets')
    gainLabel = qt.QLabel('Gain:')
    gainLabel.setObjectName('presets')
    
    self.ultrasoundPresetsLayout.addWidget(depthLabel, 1, 0, 1, 1)
    self.ultrasoundPresetsLayout.addWidget(self.depthSlider, 1, 1, 1, 5)
    self.ultrasoundPresetsLayout.addWidget(focusLabel, 2, 0, 1, 1)
    self.ultrasoundPresetsLayout.addWidget(self.focusSlider, 2, 1, 1, 5)
    self.ultrasoundPresetsLayout.addWidget(dynamicRangeLabel, 3, 0, 1, 1)
    self.ultrasoundPresetsLayout.addWidget(self.dynamicRangeSlider, 3, 1, 1, 5)
    self.ultrasoundPresetsLayout.addWidget(frequencyLabel, 4, 0, 1, 1)
    self.ultrasoundPresetsLayout.addWidget(self.frequencySlider, 4, 1, 1, 5)
    self.ultrasoundPresetsLayout.addWidget(gainLabel, 5, 0, 1, 1)
    self.ultrasoundPresetsLayout.addWidget(self.gainSlider, 5, 1, 1, 5)
    
    self.presetsWidget = qt.QWidget()
    self.presetsWidget.setContentsMargins(5, 5, 5, 5)
    self.presetsWidget.setObjectName('presetsWidget')
    self.presetsWidget.setLayout(self.ultrasoundPresetsLayout)
  
    vbox = qt.QVBoxLayout()
    vbox.setContentsMargins(0, 0, 0, 10)
    vbox.addWidget(self.presetsWidget)
    ultrasoundControlsAndZoomFrame = qt.QFrame()
    ultrasoundControlsAndZoomFrame.setLayout(vbox)
    ultrasoundControlsAndZoomFrame.setObjectName("sidePanelWidgetFrame")
    self.ultrasoundLayout.addWidget(ultrasoundControlsAndZoomFrame)

  def __del__(self):#common
    self.preCleanup()


  # Clean up when guidelet is closed
  def preCleanup(self):#common
    Guidelet.preCleanup(self)
    logging.debug('preCleanup')


  def setupConnections(self):
    logging.debug('ScoliUs.setupConnections()')
    Guidelet.setupConnections(self)
    self.calibrationCollapsibleButton.connect('toggled(bool)', self.onPatientSetupPanelToggled)
    self.exampleButton.connect('clicked(bool)', self.onExampleButtonClicked)


  def setupScene(self): #applet specific
    parameterNode = self.logic.getParameterNode()
    
    Guidelet.setupScene(self)

    moduleDir = os.path.dirname(slicer.modules.usneedleguide.path)

    # Load transform

    probeModelToImageFullpath = os.path.join(moduleDir, 'Resources', self.PROBEMODEL_TO_IMAGE_FILENAME)
    probeModelToImageNode = slicer.mrmlScene.GetFirstNodeByName(self.PROBEMODEL_TO_IMAGE)
    if probeModelToImageNode is None:
      probeModelToImageNode = slicer.util.loadTransform(probeModelToImageFullpath)
      probeModelToImageNode.SetName(self.PROBEMODEL_TO_IMAGE)
    parameterNode.SetNodeReferenceID(self.PROBEMODEL_TO_IMAGE, probeModelToImageNode.GetID())
    
    # Load models
    
    modelFileNames = ['Guide06cm', 'Guide08cm', 'Guide10cm', 'Guide12cm']
    for i in range(len(modelFileNames)):
      modelNode = parameterNode.GetNodeReference(modelFileNames[i])
      if modelNode is None:
        fileName = modelFileNames[i]
        modelFullpath = os.path.join(moduleDir, 'Resources', fileName + '.vtk')
        modelNode = slicer.util.loadModel(modelFullpath)
        displayNode = modelNode.GetDisplayNode()
        displayNode.SetVisibility(True)
        displayNode.SetColor(self.GUIDECOLORS[i][0], self.GUIDECOLORS[i][1], self.GUIDECOLORS[i][2])
        displayNode.SetSliceIntersectionVisibility(True)
        displayNode.SetSliceIntersectionThickness(2)
        modelNode.SetAndObserveTransformNodeID(probeModelToImageNode.GetID())
        parameterNode.SetNodeReferenceID(modelFileNames[i], modelNode.GetID())

    # Hide slice view annotations (patient name, scale, color bar, etc.) as they
    # decrease reslicing performance by 20%-100%
    import DataProbe
    dataProbeUtil=DataProbe.DataProbeLib.DataProbeUtil()
    dataProbeParameterNode=dataProbeUtil.getParameterNode()
    dataProbeParameterNode.SetParameter('showSliceViewAnnotations', '0')


  def disconnect(self):#TODO see connect
    logging.debug('ScoliUs.disconnect()')
    Guidelet.disconnect(self)

    # Remove observer to old parameter node
    
    self.calibrationCollapsibleButton.disconnect('toggled(bool)', self.onPatientSetupPanelToggled)
    self.exampleButton.disconnect('clicked(bool)', self.onExampleButtonClicked)


  def patientSetupPanel(self):
    logging.debug('patientSetupPanel')

    self.calibrationCollapsibleButton.setProperty('collapsedHeight', 20)
    self.calibrationCollapsibleButton.text = 'Calibration'
    # self.sliceletPanelLayout.addWidget(self.calibrationCollapsibleButton)

    self.calibrationButtonLayout = qt.QFormLayout(self.calibrationCollapsibleButton)
    self.calibrationButtonLayout.setContentsMargins(12, 4, 4, 4)
    self.calibrationButtonLayout.setSpacing(4)

    self.exampleButton = qt.QPushButton("Example button")
    self.exampleButton.setCheckable(False)
    self.calibrationButtonLayout.addRow(self.exampleButton)


  def onExampleButtonClicked(self, toggled):
    logging.debug('onExampleButtonClicked')


  def onPatientSetupPanelToggled(self, toggled):
    if toggled == False:
      return

    logging.debug('onPatientSetupPanelToggled: {0}'.format(toggled))

    self.selectView(self.VIEW_ULTRASOUND)

	
  def onUltrasoundPanelToggled(self, toggled):
    if not toggled:
      # deactivate placement mode
      interactionNode = slicer.app.applicationLogic().GetInteractionNode()
      interactionNode.SetCurrentInteractionMode(interactionNode.ViewTransform)
      return

    logging.debug('onUltrasoundPanelToggled: {0}'.format(toggled))

    # self.selectView(self.VIEW_ULTRASOUND_3D)
    self.selectView(self.VIEW_ULTRASOUND)

    # The user may want to freeze the image (disconnect) to make contouring easier.
    # Disable automatic ultrasound image auto-fit when the user unfreezes (connect)
    # to avoid zooming out of the image.
    self.fitUltrasoundImageToViewOnConnect = not toggled


  def getCamera(self, viewName):
    """
    Get camera for the selected 3D view
    """
    camerasLogic = slicer.modules.cameras.logic()
    camera = camerasLogic.GetViewActiveCameraNode(slicer.mrmlScene.GetFirstNodeByName(viewName))
    return camera


  def getViewNode(self, viewName):
    """
    Get the view node for the selected 3D view
    """
    viewNode = slicer.mrmlScene.GetFirstNodeByName(viewName)
    return viewNode


  def updateNavigationView(self):
    self.selectView(self.navigationView)

    # Reset orientation marker
    if hasattr(slicer.vtkMRMLViewNode(),'SetOrientationMarkerType'): # orientation marker is not available in older Slicer versions
      v1=slicer.mrmlScene.GetFirstNodeByName('View1')
      v1.SetOrientationMarkerType(v1.OrientationMarkerTypeNone)