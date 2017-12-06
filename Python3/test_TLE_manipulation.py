for i in sorted(os.listdir()):
  if bool(re.search('^\d{4}\.txt$', i)):
    print(i)
    TLE.dump_to_file(TLE.extract_amsat_TLE(i))
  else:
    print(i, ': skipped')
