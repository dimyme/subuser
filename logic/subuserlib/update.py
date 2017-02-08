# -*- coding: utf-8 -*-

"""
High level operations used for updating, rolling back, locking ect.
"""

#external imports
import sys
#internal imports
import subuserlib.verify

#####################################################################################
def all(user,permissionsAccepter,prompt=False,useCache=False):
  """
  This command updates(if needed) all of the installed subuser images.
  """
  user.getRegistry().log("Updating...")
  for _,repository in user.getRegistry().repositories.items():
    repository.updateSources()
  subusers = user.getRegistry().subusers.getSortedList()
  subuserlib.verify.verify(user,checkForUpdatesExternally=True,useCache=useCache,subusers=subusers,permissionsAccepter=permissionsAccepter,prompt=prompt)
  user.getRegistry().commit()

def subusers(user,subusers,permissionsAccepter,prompt=False,useCache=False):
  """
  This command updates the specified subusers' images.
  """
  user.getRegistry().log("Updating...")
  for _,repository in user.getRegistry().repositories.items():
    repository.updateSources()
  subuserlib.verify.verify(user,subusers=subusers,useCache=useCache,checkForUpdatesExternally=True,permissionsAccepter=permissionsAccepter,prompt=prompt)
  user.getRegistry().commit()

def lockSubuser(user,subuser,commit):
  """
  Lock the subuser to the image and permissions that it had at a given registry commit.
  """
  from subuserlib.classes.user import User
  from subuserlib.classes.registry import Registry
  oldUser = User(name=user.name,homeDir=user.homeDir)
  oldUser.setRegistry(Registry(oldUser,gitReadHash=commit,ignoreVersionLocks=True,initialized=True))
  if not oldUser.getRegistry().gitRepository.doesCommitExist(commit):
    sys.exit("Commit "+commit+" does not exist. Cannot lock to commit.")
  try:
    oldSubuser = oldUser.getRegistry().subusers[subuser.name]
  except KeyError:
    sys.exit("Subuser, "+subuser.name+" did not exist yet at commit "+commit+". Cannot lock to commit.")
  subuser.imageId = oldSubuser.imageId
  oldSubuser.permissions.save()
  oldSubuser.getPermissionsTemplate().save()
  user.getRegistry().logChange("Locking subuser "+subuser.name+" to commit: "+commit)
  user.getRegistry().logChange("New image id is "+subuser.imageId)
  subuser.locked = True
  subuserlib.verify.verify(user)
  user.getRegistry().commit()

def unlockSubuser(user,subuser,permissionsAccepter,prompt):
  """
  Unlock the subuser, leaving it to have an up to date image.  Delete user set permissions if unlockPermissions is True.
  """
  if subuser.locked:
    user.getRegistry().logChange("Unlocking subuser "+subuser.name)
    subuser.locked = False
    subuserlib.verify.verify(user,subusers=[subuser],checkForUpdatesExternally=True,permissionsAccepter=permissionsAccepter,prompt=prompt)
    user.getRegistry().commit()
  else:
    user.getRegistry().log("Subuser "+subuser.name + " is not locked. Doing nothing.")
