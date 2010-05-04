import os
import zipfile

import simplejson as json

def build_xpi(template_root_dir, manifest, xpi_name,
              harness_options, xpts, main_package_dir):
    zf = zipfile.ZipFile(xpi_name, "w", zipfile.ZIP_DEFLATED)

    open('.install.rdf', 'w').write(str(manifest))
    zf.write('.install.rdf', 'install.rdf')
    os.remove('.install.rdf')

    IGNORED_FILES = [".hgignore", "install.rdf", 
                     "application.ini", xpi_name]
    IGNORED_FILE_SUFFIXES = ["~"]
    IGNORED_DIRS = [".svn", ".hg", "defaults"]

    def filter_filenames(filenames):
        for filename in filenames:
            if filename in IGNORED_FILES:
                continue
            if any([filename.endswith(suffix)
                    for suffix in IGNORED_FILE_SUFFIXES]):
                continue
            yield filename

    for dirpath, dirnames, filenames in os.walk(template_root_dir):
        filenames = list(filter_filenames(filenames))
        dirnames[:] = [dirname for dirname in dirnames
                       if dirname not in IGNORED_DIRS]
        for filename in filenames:
            abspath = os.path.join(dirpath, filename)
            arcpath = abspath[len(template_root_dir)+1:]
            zf.write(abspath, arcpath)

    for abspath in xpts:
        zf.write(str(abspath),
                 str(os.path.join('components',
                                  os.path.basename(abspath))))

    ### NOTE: copy into the xpi all the legacy chrome stuff (chrome.manifest and chrome dirs)
    source_chrome_manifest = os.path.join(main_package_dir,'chrome.manifest')
    source_chrome_dir = os.path.join(main_package_dir,'chrome')
    source_default_prefs = os.path.join(main_package_dir,'default_prefs.js')

    if os.path.exists(source_chrome_manifest):        
        zf.write(str(source_chrome_manifest), 'chrome.manifest')

    if os.path.exists(source_default_prefs):        
        zf.write(str(source_default_prefs), os.path.join("default", "preferences", "default_prefs.js"))

    if os.path.exists(source_chrome_dir):
        abs_dirname = source_chrome_dir

        import re
        backup_files_rx = re.compile(".*~")

        for dirpath, dirnames, filenames in os.walk(abs_dirname):
            goodfiles = [filename for filename in filenames
                         if not backup_files_rx.search(filename)]
            for filename in goodfiles:
                abspath = os.path.join(dirpath, filename)
                arcpath = abspath[len(abs_dirname)+1:]
                arcpath = os.path.join("chrome", arcpath)
                zf.write(str(abspath), str(arcpath))            
                dirnames[:] = [dirname for dirname in dirnames
                               if dirname not in IGNORED_DIRS]
    ### END legacy chrome stuff 

    new_resources = {}
    for resource in harness_options['resources']:
        base_arcpath = os.path.join('resources', resource)
        new_resources[resource] = ['resources', resource]
        abs_dirname = harness_options['resources'][resource]
        for dirpath, dirnames, filenames in os.walk(abs_dirname):
            goodfiles = list(filter_filenames(filenames))
            for filename in goodfiles:
                abspath = os.path.join(dirpath, filename)
                arcpath = abspath[len(abs_dirname)+1:]
                arcpath = os.path.join(base_arcpath, arcpath)
                zf.write(str(abspath), str(arcpath))
            dirnames[:] = [dirname for dirname in dirnames
                           if dirname not in IGNORED_DIRS]
    harness_options['resources'] = new_resources

    open('.options.json', 'w').write(json.dumps(harness_options))
    zf.write('.options.json', 'harness-options.json')
    os.remove('.options.json')

    zf.close()
