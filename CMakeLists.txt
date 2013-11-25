cmake_minimum_required(VERSION 2.8.9)

#-----------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
  set(EXTENSION_NAME XNATSlicer)
  set(EXTENSION_HOMEPAGE "http://www.slicer.org/slicerWiki/index.php/Documentation/4.3/Extensions/XNATSlicer")
  set(EXTENSION_CATEGORY "Remote")
  set(EXTENSION_CONTRIBUTORS "Sunil Kumar (Moka Creative LLC, Washington University in St. Louis), Dan Marcus (Washington University in St. Louis), Steve Pieper (Isomics)")
  set(EXTENSION_DESCRIPTION "Secure GUI-based IO with any XNAT server.")
  set(EXTENSION_ICONURL "https://raw.github.com/skumar221/XNATSlicer/master/XnatSlicer/Resources/Icons/XNATSlicer-MarketIcon.png")
  set(EXTENSION_SCREENSHOTURLS "https://raw.github.com/skumar221/XNATSlicer/master/XnatSlicer/Resources/Images/UserDesc_MainPanel.png")
endif()

#-----------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
  find_package(Slicer REQUIRED)
  include(${Slicer_USE_FILE})
endif()

#-----------------------------------------------------------------------------
add_subdirectory(XNATSlicer)

#-----------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
  include(${Slicer_EXTENSION_CPACK})
endif()
