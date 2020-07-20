import os
from __main__ import vtk, qt, ctk, slicer

from Guidelet import GuideletLoadable, GuideletLogic, GuideletTest, GuideletWidget
from Guidelet import Guidelet
import logging
import time


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
                   'LiveUltrasoundNodeName': 'Image_Reference',
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

  def __init__(self, parent, logic, configurationName='Default'):
    self.calibrationCollapsibleButton = None

    Guidelet.__init__(self, parent, logic, configurationName)
    logging.debug('UsNeedleGuideGuidelet.__init__')

    self.logic.addValuesToDefaultConfiguration()

    moduleDirectoryPath = slicer.modules.usneedleguide.path.replace('UsNeedleGuide.py', '')

    # Set up main frame.

    self.sliceletDockWidget.setObjectName('UsNeedleGuidePanel')
    self.sliceletDockWidget.setWindowTitle('Example guidelet')
    self.mainWindow.setWindowTitle('UsNeedleGuide')
    self.mainWindow.windowIcon = qt.QIcon(moduleDirectoryPath + '/Resources/Icons/UsNeedleGuide.png')

    self.setupScene()

    self.navigationView = self.VIEW_ULTRASOUND_3D

    # Setting button open on startup.
    self.calibrationCollapsibleButton.setProperty('collapsed', False)


  def createFeaturePanels(self):
    # Create GUI panels.

    self.calibrationCollapsibleButton = ctk.ctkCollapsibleButton()
    self.patientSetupPanel()

    featurePanelList = Guidelet.createFeaturePanels(self)

    featurePanelList[len(featurePanelList):] = [self.calibrationCollapsibleButton]

    return featurePanelList


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
    logging.debug('setupScene')

    '''
    ReferenceToRas transform is used in almost all IGT applications. Reference is the coordinate system
    of a tool fixed to the patient. Tools are tracked relative to Reference, to compensate for patient
    motion. ReferenceToRas makes sure that everything is displayed in an anatomical coordinate system, i.e.
    R, A, and S (Right, Anterior, and Superior) directions in Slicer are correct relative to any
    images or tracked tools displayed.
    ReferenceToRas is needed for initialization, so we need to set it up before calling Guidelet.setupScene().
    '''

    self.referenceToRas = slicer.mrmlScene.GetFirstNodeByName('ReferenceToRas')
    if not self.referenceToRas:
      self.referenceToRas=slicer.vtkMRMLLinearTransformNode()
      self.referenceToRas.SetName("ReferenceToRas")
      m = self.logic.readTransformFromSettings('ReferenceToRas', self.configurationName)
      if m is None:
        m = self.logic.createMatrixFromString('1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1')
      self.referenceToRas.SetMatrixTransformToParent(m)
      slicer.mrmlScene.AddNode(self.referenceToRas)

    Guidelet.setupScene(self)

    # Transforms

    logging.debug('Create transforms')

    '''
    In this example we assume that there is a tracked needle in the system. The needle is not
    tracked at its tip, so we need a NeedleTipToNeedle transform to define where the needle tip is.
    In your application Needle may be called Stylus, or maybe you don't need such a tool at all.
    '''

    self.needleToReference = slicer.mrmlScene.GetFirstNodeByName('NeedleToReference')
    if not self.needleToReference:
      self.needleToReference = slicer.vtkMRMLLinearTransformNode()
      self.needleToReference.SetName('NeedleToReference')
      slicer.mrmlScene.AddNode(self.needleToReference)

    self.needleTipToNeedle = slicer.mrmlScene.GetFirstNodeByName('NeedleTipToNeedle')
    if not self.needleTipToNeedle:
      self.needleTipToNeedle = slicer.vtkMRMLLinearTransformNode()
      self.needleTipToNeedle.SetName('NeedleTipToNeedle')
      m = self.logic.readTransformFromSettings('NeedleTipToNeedle', self.configurationName)
      if m:
        self.needleTipToNeedle.SetMatrixTransformToParent(m)
      slicer.mrmlScene.AddNode(self.needleTipToNeedle)

    # Models
    logging.debug('Create models')

    self.needleModel = slicer.mrmlScene.GetFirstNodeByName('NeedleModel')
    if not self.needleModel:
      self.needleModel = slicer.modules.createmodels.logic().CreateNeedle(80, 1.0, 2.5, 0)
      self.needleModel.SetName('NeedleModel')

    # Build transform tree
    logging.debug('Set up transform tree')

    self.needleToReference.SetAndObserveTransformNodeID(self.referenceToRas.GetID())
    self.needleTipToNeedle.SetAndObserveTransformNodeID(self.needleToReference.GetID())
    self.needleModel.SetAndObserveTransformNodeID(self.needleTipToNeedle.GetID())

    # Hide slice view annotations (patient name, scale, color bar, etc.) as they
    # decrease reslicing performance by 20%-100%
    logging.debug('Hide slice view annotations')
    import DataProbe
    dataProbeUtil=DataProbe.DataProbeLib.DataProbeUtil()
    dataProbeParameterNode=dataProbeUtil.getParameterNode()
    dataProbeParameterNode.SetParameter('showSliceViewAnnotations', '0')


  def disconnect(self):#TODO see connect
    logging.debug('ScoliUs.disconnect()')
    Guidelet.disconnect(self)

    # Remove observer to old parameter node
    if self.patientSLandmarks_Reference and self.patientSLandmarks_ReferenceObserver:
      self.patientSLandmarks_Reference.RemoveObserver(self.patientSLandmarks_ReferenceObserver)
      self.patientSLandmarks_ReferenceObserver = None

    self.calibrationCollapsibleButton.disconnect('toggled(bool)', self.onPatientSetupPanelToggled)
    self.exampleButton.disconnect('clicked(bool)', self.onExampleButtonClicked)


  def patientSetupPanel(self):
    logging.debug('patientSetupPanel')

    self.calibrationCollapsibleButton.setProperty('collapsedHeight', 20)
    self.calibrationCollapsibleButton.text = 'Calibration'
    self.sliceletPanelLayout.addWidget(self.calibrationCollapsibleButton)

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

    self.selectView(self.VIEW_ULTRASOUND_3D)

	
  def onUltrasoundPanelToggled(self, toggled):
    if not toggled:
      # deactivate placement mode
      interactionNode = slicer.app.applicationLogic().GetInteractionNode()
      interactionNode.SetCurrentInteractionMode(interactionNode.ViewTransform)
      return

    logging.debug('onUltrasoundPanelToggled: {0}'.format(toggled))

    self.selectView(self.VIEW_ULTRASOUND_3D)

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