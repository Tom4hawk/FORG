rem This is a batch file written to install the FORG on windows systems.
rem But since I haven't used windows or DOS in quite a while, it may be
rem completely broken.  Please let me know if it is.  :)
rem David Allen <mda@idatar.com>
rem
rem Don't try to run this if you're not on a machine that has some
rem form of DOS installed.  :)

rem Create the options directory:
md c:\forg-data
copy default-bookmarks.xml c:\forg-data\bookmarks

rem Install the program in C:\FORG
md c:\FORG
copy *.py c:\FORG



