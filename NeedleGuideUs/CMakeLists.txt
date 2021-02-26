cmake_minimum_required(VERSION 3.13.4)

project(NeedleGuideUs)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/NeedleGuideUs")
set(EXTENSION_CATEGORY "Ultrasound")
set(EXTENSION_CONTRIBUTORS "Tamas Ungi (Queen's University)")
set(EXTENSION_DESCRIPTION "Needle guide applications for ultrasound")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/NeedleGuideUs.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/NeedleGuideUs/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(NeedleGuide)
add_subdirectory(UsNeedleGuideGuidelet)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
