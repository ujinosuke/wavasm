# makemake.py
#    python script for auto make makefile
#!/usr/bin/env python

import os
import sys
import traceback


#------------ VERSION -----------------------
version = '0.1.1'

#------------ HTML Style -----------------------

htmlColorMap = {
'def' : 'gray',	# default
'src' : 'blue' ,
'inc' : 'green' ,
'obj' : 'gray' ,
'cnf' : 'red' ,
}

#------------ DEFAULT -----------------------
mkTarget = 'index.html'
mkProjectRoot = '.'
mkLink = '$(LINKER) $(LDFLAGS) -o $(OUTDIR)/$(TARGET) $^'
mkSrcPaths = []
mkOmitSrc = []
mkIndivisualRule = {} 
mkConfigurations = {}

mkDefine = {
'CC':'emcc',
'LINKER':'emcc',
'CFLAGS':'-O0 -g',
'LDFLAGS':'-lm',
'INCLUDE':'',
'OUTDIR':'obj',
}

mkSuffixRule = {
'.c'  : '$(CC) $(INCLUDE) $(CFLAGS) -c $< -o $@',
'.cpp': '$(CC) $(INCLUDE) $(CFLAGS) -c $< -o $@',
'.cc' : '$(CC) $(INCLUDE) $(CFLAGS) -c $< -o $@',
'.S'  : '$(CC) $(INCLUDE) -c $< -o $@',
'.s'  : '$(CC) $(INCLUDE) -c $< -o $@',
'.asm': '$(CC) $(INCLUDE) -c $< -o $@',
}

mkHeader = {
'.h',
'.hpp',
'.inc',
}

#---------- FIXED -------------------------------

fxMapOmitExt = [ '.o' , '.d' , '.d0' , '.d1' ]
fxConfigCmd = 'conf'
fxDirmapFile = 'dirmap.html'

#---------- RESULT -------------------------------

resultAllSrc = []
resultAllInc = []
resultConflict = []

#----- Error
def raiseError( str ):
	print('--------------------')
	print('makemake.py: ERROR')
	print( str )
	print('--------------------')
	raise ValueError

#----- Help Functions
def stripSpaceTab( line ):
	line = line.replace(' ','')
	line = line.replace('\t','')
	return line

def getFileBodyAndExt( path ):
	filebody = os.path.splitext( os.path.basename( path ) )
	return filebody[0], filebody[1]

def getFilename( path ):
	return os.path.basename( path ) 

def getDirLevel( directory ):
	return len( directory.split('\\' )) -1

def repairPaths( path ): return path if path[0] == '.' else '.\\'+path

#---------- CDirNode ... Directory Node ----------
class CDirNode:

		def __init__(self, path):
			self.parent = None
			self.children = []
			self.path = path
			self.src = False
			self.inc = False
			self.markOmit = False

		def setMarkOmitChildren(self, paths):
			possibleOmit = False
			for child in self.children:
				if child.getPath() in paths:
					possibleOmit = True
					break
			if possibleOmit:
				for child in self.children: child.markOmit = True


		def setSrc(self): self.src = True
		def setInc(self): self.inc = True
		def getParent(self): return self.parent
		def getPath(self): return self.path
		def getSrc(self): return self.src
		def getInc(self): return self.inc
		def getChildren(self): return self.children
		def getMarkOmit(self): return self.markOmit

		def getParentPath(self):
			if mkProjectRoot == self.getPath(): return None
			ret = ''
			parts = self.path.split('\\')
			for i in range( len( parts ) -1):
				ret+=parts[i]
				ret+='\\'
			ret = ret.rstrip('\\')
			return ret

		def getRelationship(self, nodes):

			# search parent
			if self.getPath() != mkProjectRoot:
				parent = self.getParentPath()
				for node in nodes:
					if node.getPath() == parent:
						self.parent = node

			# search children
			for node in nodes:
				parent = node.getParentPath()
				if parent != None and parent == self.getPath():
					self.children.append( node )


		@classmethod
		def searchNodeByPath( cls, nodes, path):
			for node in nodes:
				if node.getPath() == path:
					return node
			return None


#----- PROCESSING!
def processPharse():

	# Relative  ... auto fixed
	for i in range(len(mkSrcPaths)): mkSrcPaths[i] = repairPaths( mkSrcPaths[i] )
	for i in range(len(mkOmitSrc)): mkOmitSrc[i] = repairPaths( mkOmitSrc[i] )

	# Indivisual Rule ... auto fixed
	keys = mkIndivisualRule.keys()
	for i in range(len(keys)):
		key = keys[i]
		rkey = repairPaths( key )
		if mkIndivisualRule.has_key( rkey ) == False:
			rule = mkIndivisualRule[ key ]
			del mkIndivisualRule[ key ]
			mkIndivisualRule[ rkey ] = rule

	# srcPaths check

	if len(mkSrcPaths) == 0: mkSrcPaths.append( mkProjectRoot )

	# make directory node

	dirNode = []
	for root, dirs, files in os.walk(mkProjectRoot):
		dirNode.append( CDirNode( root ) )

	# get parent and children
	
	for node in dirNode:
		node.getRelationship( dirNode )

	# get src path

	for node in dirNode:
		path = node.getPath()
		node.setMarkOmitChildren( mkSrcPaths )
		if path in mkSrcPaths:
			node.setSrc()
		else:
			parent = node.getParent()
			if parent == None or node.getMarkOmit(): pass
			elif parent.getSrc(): node.setSrc()

	# get src list
	
	for node in dirNode:
		
		if node.getSrc():
			
			files = os.listdir( node.getPath() )
			for a in files:
				ext = os.path.splitext( a )[1]
				pathSrc = node.getPath() + '\\' + a
				if pathSrc in mkOmitSrc: continue
				if ext in mkSuffixRule:
					resultAllSrc.append( pathSrc )
				if ext in mkHeader:
					node.setInc()
			if node.getInc():
				resultAllInc.append( node.getPath() )

def checkConflict():
	tmp = []
	conflictBody = []
	for path in resultAllSrc:
		body, ext = getFileBodyAndExt( path )
		if body in tmp:
			conflictBody.append( body )
		tmp.append( body )

	for path in resultAllSrc:
		body, ext = getFileBodyAndExt( path )
		if body in conflictBody:
			resultConflict.append( path )
			
def checkValue():

	# Check no object

	if len(resultAllSrc) == 0:
		raiseError( 'NO Obj' )
		
	# Check same name object
	if len(resultConflict):
		msg = 'Object Conflict\n'
		for path in resultConflict: msg += path + '\n'
		raiseError( msg )

		
def printMakefile( output, argv, config ):

	fp = open( output, 'w' )
	bkup = sys.stdout
	sys.stdout = fp

	print('#-----------------------------------------------------')
	print('#-- this file is auto generated by makemake.py')
	print('#--                      copyright ujinosuke')
	print('#-----------------------------------------------------')

	# SETTING

	print('\n#-- Setting')
	for val in mkDefine:
		print('%s %s %s' % (val,'=',mkDefine[ val ]) )

	# TARGET
	print('TARGET = %s\n' % mkTarget )

	# INCLUDE

	print('\n#-- Include')
	print('INCLUDE +=\\')
	for i in range(len(resultAllInc)):
		cmd = '-I'+resultAllInc[i];
		print(cmd if i == len(resultAllInc) -1 else cmd + ' \\' )

	# OBJECTS
	print('\n#-- Objects')
	print('OBJS =\\')
	for i in range(len(resultAllSrc)):
		cmd = '$(OUTDIR)/%s.o' % os.path.splitext(os.path.basename( resultAllSrc[i] ) )[0]
		print( cmd if i == len(resultAllSrc) -1 else cmd + ' \\' )

	# TARGET
	print('\n#-- TARGET')
	print('all: $(OUTDIR) depend $(OUTDIR)/$(TARGET)')
	print('$(OUTDIR)/$(TARGET): $(OBJS)')
	print('\t%s\n' % mkLink )

	# Souce code
	for path in resultAllSrc:
		filebody, ext = getFileBodyAndExt( path )
		rule = mkIndivisualRule[path] if path in mkIndivisualRule else mkSuffixRule[ext]
		print('$(OUTDIR)/%s.o: %s' % (filebody, path) )
		print('\t%s' % rule )
		print('\n$(OUTDIR)/%s.d: %s' % (filebody, path) )
		print('\t%s -MM' % rule )
		print('\t@sed -e \'1s/^/%s/g\' $@ > $@.d0' % (mkDefine['OUTDIR']) )
		print('\t@sed -e \'s/.o/.d/g\' $@.d0 > $@.d1\n')

	# Footer

	print('$(OUTDIR):')
	print('\tmkdir $@')
	print('.PHNOY: depend clean make %s' % fxConfigCmd)
	print('clean:')
	print('\t@echo ---- clean project -----')
	print('\tdel $(OUTDIR)\*.d $(OUTDIR)\*.d0 $(OUTDIR)\*.d1 $(OUTDIR)\*.o $(OUTDIR)\$(TARGET)' )
	print('depend: $(OBJS:.o=.d)')
	print('')
	print('-include $(OUTDIR)\*.d0')
	print('-include $(OUTDIR)\*.d1')
	print('')

	# self build
	print('make:')
	makecmd = ''; 
	for str in argv: makecmd += str + ' '
	print('\tpython %s\n' % makecmd )

	# switch configuration
	makecmd = ''
	bNextOmit = False
	for str in argv:
		if str == '-c':	bNextOmit = True
		elif bNextOmit: bNextOmit = False
		else: makecmd += str + ' '

	for i in range(len(mkConfigurations)):
		print('%s.%s:' % (fxConfigCmd, mkConfigurations.keys()[i]) )
		print('\tpython %s -c %s\n' % (makecmd, mkConfigurations.keys()[i]) )

	# show config

	if  config != '':
		print('%s:\n\t@echo Active configuration : %s\n' % ( fxConfigCmd, config ) )
	else:
		print('%s:\n\t@echo no configuration project\n' % fxConfigCmd )

	sys.stdout = bkup
	fp.close()

	print ('Create Makefile Complete -> %s' % output)


#----- class

def procNutral( line ):
	return True

def procSetting( line ):
	if line.find('+=') != -1:
		pair = line.split('+=')
		pair[0] = stripSpaceTab( pair[0] )
		body = mkDefine[ pair[0] ]
		mkDefine[ pair[0] ] = body + pair[1]
	else:
		pair = line.split('=')
		pair[0] = stripSpaceTab( pair[0] )
		mkDefine[ pair[0] ] = '' if len(pair) == 1 else pair[1]
	return True

def procPaths( line ):
	line = stripSpaceTab( line )
	mkSrcPaths.append( line )
	return True

def procTarget( line ):
	global mkTarget
	line = stripSpaceTab( line )
	mkTarget = line
	return True

def procRoot( line ):
	global mkProjectRoot
	line = stripSpaceTab( line )
	mkProjectRoot = line
	return True

def procOmit( line ):
	line = stripSpaceTab( line )
	mkOmitSrc.append(line)
	return True

def procRule( line ):
	line = line.split(':')
	ext = stripSpaceTab(line[0])
	rule = line[1].lstrip(' \t')
	if ext[0] == '.':
		mkSuffixRule[ ext ] = rule
	else:
		raiseError('[rule] ERROR, must be extention')
	return True

def procIndiRule( line ):
	line = line.split(':')
	path = stripSpaceTab(line[0])
	rule = line[1].lstrip(' \t')
	mkIndivisualRule[path] = rule
	return True

def procConfiguration( line ):
	line = stripSpaceTab(line).split(':')
	mkConfigurations[ line[0] ] = line[1]
	return True

keywords = {
'': procNutral,
'[define]': procSetting,
'[src path]': procPaths,
'[target]': procTarget,
'[root]': procRoot,
'[omit]': procOmit,
'[rule]': procRule,
'[indivisual rule]' : procIndiRule,
'[configuration]' : procConfiguration,
}



def inputConfig( fp ):
	lines = fp.readlines()

	pharseStat_OK = True
	mode = ''
	for line in lines:
		line = line.lstrip(" \t")
		line = line.rstrip(" \t\n")
		if len(line) == 0: continue
		
		if line.startswith('#') == False:

			# mode change operation

			if line.startswith('['):
				if line in keywords:
					mode = line
					continue
				else:
					raiseError('Invalid derective: %s' % line)
			# phaseing
			
			ret = keywords[ mode ]( line )
			if ret == False:
				pharseStat_OK = False
				break

	if pharseStat_OK == False:
		print('Input file Error')


def createMapFile( output ):

	#resultAllSrc = []
	#resultAllInc = []
	#resultConflict = []
	fp = open( output, 'w' )
	bkup = sys.stdout
	sys.stdout = fp

	print('<HTML>')
	print('  <HEAD>')
	print('    <TITLE> Source Code Tree</TITLE>')
	print('  </HEAD>')
	print('  <BODY>')

	# tytle
	abspath = os.path.dirname( os.path.abspath( __file__ ) )

	print('<font size=\"6\"><center># (%s)%s</center></font>' % (abspath ,mkProjectRoot  ))
	print('<br><font color=\"%s\">Source Code is indicated by this color</font><br>' % htmlColorMap['src'] )
	print('<br><font color=\"%s\">Header file is indicated by this color</font><br>' % htmlColorMap['inc'] )
	print('<br><hr>')

	for root, dirs, files in os.walk(mkProjectRoot):
		level = getDirLevel( root )
		space = ''
		dirspace = ''
		for i in range(level): space += '  '
		bInc = root in resultAllInc
		if bInc:
			print ( '<br><pre><font color=\"%s\">%s ==== INCLUDE </font></pre><br>' % ( htmlColorMap['inc'], root ) )
		else:
			print ( '<br><pre>%s</pre><br>' % ( root ) )
		for f in files:
			colorStyle = 'def'
			path = os.path.join(root,f)
			body, ext = getFileBodyAndExt( path )
			msg = '<pre><font color=\"%s\">%s- %s'
			if path in resultConflict: msg += ' ---Conflict!'; colorStyle = 'cnf'
			elif path in resultAllSrc: colorStyle = 'src'
			elif bInc and ext in mkHeader: colorStyle = 'inc'
			elif ext in fxMapOmitExt: colorStyle = 'obj'
			
			print ( (msg + '</font></pre>') % (htmlColorMap[colorStyle], space, getFilename( path )  ) )

	print('  </BODY>')
	print('</HTML>')

	sys.stdout = bkup
	fp.close()

def createMakefile( output , argv , config , mapfile):

	# PROCESSING!!!

	processPharse()

	# Check Conflict

	checkConflict()

	# create mapfile

	if mapfile != '':
		createMapFile( mapfile )
		
	# Check Value

	checkValue()

	# PRINTING!!!

	printMakefile( output, argv , config)

def printHelp():
	print('makemake.py help')
	print('Create makefile File script, powered by Python')
	print('usage: python makemake.py [option]')
	print('\n--- [option]\n')
	print('-o [file]\toutput file (default: makefile)')
	print('-f [file]\tinput make configuration file (default: None )')
	print('-m\t\tcreate directory map html file')
	print('-verbose\tverbose option')
	print('-h\t\tshow help')
	print('-v\t\tshow version')
	print('\n--- [make configuration file]\n')

def printVer():
	print('makemake.py version %s' % version )

def main():

	commands = {
	'-o' : 'makefile',	# outputfile
	'-f' : '',		# inputfile
	'-c' : '',		# configuration
	'-h' : False,		# showHelp
	'-v' : False,		# showVersion
	'-m' : False,		# create dir map html
	'-verbose' : False,	# verborse
	}

	argv = sys.argv
	argc = len(argv)

	try:
		i = 1
		while i < argc:
			val = commands[ argv[i] ]
			if isinstance( val, str ):
				commands[ argv[i] ] = argv[i+1]
				i+=1
			elif isinstance( val, bool ):
				commands[ argv[i] ] = True
			elif isinstance( val, int ):
				commands[ argv[i] ] = int(argv[i+1])
				i+=1
			i+=1
	except:
		print('Command error, type below for help')
		print('python makemake.py -h')
		exit()

	if commands[ '-h' ]: printHelp(); exit()
	if commands[ '-v' ]: printVer(); exit()
	currentConfiguration = commands[ '-c' ]


	try:
		if commands[ '-f' ] != '':
			fp = open( commands[ '-f' ], 'r' )
			inputConfig( fp )
			fp.close()

		if len(mkConfigurations) != 0:
			
			# default configuration set
			if currentConfiguration == '': currentConfiguration = mkConfigurations.keys()[0]
			fp = open( mkConfigurations[ currentConfiguration ], 'r' )
			inputConfig( fp )
			fp.close()
			
		mpfile = fxDirmapFile if commands[ '-m'] else ''

		createMakefile( commands[ '-o' ], argv, currentConfiguration, mpfile )

	
	except IOError:
		print('makedepend.py: I/O ERROR')
	except:
		print('makedepend.py: Unexpected error: %s' % traceback.format_exc(sys.exc_info()[2] ))

if __name__ == '__main__':
	main()
