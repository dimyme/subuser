#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

import pathConfig
#external imports
import sys
#internal imports
import subuserlib.classes.user, subuserlib.run

##############################################################
helpString = """
Display the command which would be issued to launch Docker if you were to run this subuser.

For example:

    $ subuser dry-run firefox

Will display the command used to launch the subuser firefox.

Please note, this is only a rough approximation for debugging purposes and there is no guarantee that the command displayed here would actually work.
"""

#################################################################################################
def dryRunTestSetup():
  import sys,os,getpass
  os.getuid = lambda: 1000
  getpass.getuser = lambda: "travis"

def dryRun(args):
  """
  Print the command that would have been run if this wasn't a dry run.

  >>> dry_run = __import__("dry-run")
  >>> dry_run.dryRunTestSetup()
  >>> import subuser,subuserlib.classes.user
  >>> user = subuserlib.classes.user.User()
  >>> remove_old_images = __import__("remove-old-images")

  If we dry run the basic foo test subuser, we will see the generated pre-run Dockerfile and also the docker command that will launch our subuser.

  >>> dry_run.dryRun(["foo"])
  The image will be prepared using the Dockerfile:
  FROM 2
  RUN useradd --uid=1000 travis ;export exitstatus=$? ; if [ $exitstatus -eq 4 ] ; then echo uid exists ; elif [ $exitstatus -eq 9 ]; then echo username exists. ; else exit $exitstatus ; fi
  RUN test -d /home/travis || mkdir /home/travis && chown travis /home/travis
  <BLANKLINE>
  The command to launch the image is:
  docker 'run' '-i' '-t' '--rm' '--workdir=/home/travis/test-home' '-e' 'HOME=/home/travis/test-home' '--net=none' '--user=1000' 'imageId' '/usr/bin/foo'

  Running subusers installed through temporary repositories works as well.  Here, we add a subuser named bar, run it, and then remove it again.
 
  >>> subuser.subuser(user,["add","bar","bar@file:///home/travis/remote-test-repo"])
  Adding new temporary repository file:///home/travis/remote-test-repo
  Adding subuser bar bar@file:///home/travis/remote-test-repo
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Installing bar ...
  Installed new image for subuser bar
  Running garbage collector on temporary repositories...

  The actual dry-run call.

  >>> dry_run.dryRun(["bar"])
  The image will be prepared using the Dockerfile:
  FROM 4
  RUN useradd --uid=1000 travis ;export exitstatus=$? ; if [ $exitstatus -eq 4 ] ; then echo uid exists ; elif [ $exitstatus -eq 9 ]; then echo username exists. ; else exit $exitstatus ; fi
  RUN test -d /home/travis || mkdir /home/travis && chown travis /home/travis
  <BLANKLINE>
  The command to launch the image is:
  docker 'run' '-i' '-t' '--rm' '--workdir=/home/travis/test-home' '-e' 'HOME=/home/travis/test-home' '--net=none' '--user=1000' 'imageId' '/usr/bin/bar'

  Cleanup.

  >>> subuser.subuser(user,["remove","bar"])
  Removing subuser bar
   If you wish to remove the subusers image, issue the command $ subuser remove-old-images
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Running garbage collector on temporary repositories...
  >>> remove_old_images.removeOldImages(user)
  Verifying subuser configuration.
  Verifying registry consistency...
  Unregistering any non-existant installed images.
  Checking if images need to be updated or installed...
  Running garbage collector on temporary repositories...
  Removing uneeded temporary repository: file:///home/travis/remote-test-repo
  """
  if len(args) == 0 or {"help","-h","--help"} & set(args):
    print(helpString)
    sys.exit()

  subuserName = args[0]
  argsToPassToImage = args[1:]

  user = subuserlib.classes.user.User()
  if subuserName in user.getRegistry().getSubusers():
    print("The image will be prepared using the Dockerfile:")
    print(subuserlib.run.generateImagePreparationDockerfile(user.getRegistry().getSubusers()[subuserName]))
    print("The command to launch the image is:")
    print(subuserlib.run.getPrettyCommand(user.getRegistry().getSubusers()[subuserName],"imageId",argsToPassToImage))
  else:
    sys.exit(subuserName + " not found.\n"+helpString)

if __name__ == "__main__":
  dryRun(sys.argv[1:])
