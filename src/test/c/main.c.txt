#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <jansson.h>

int main(void) {

  char *gitOrigin = getenv("GIT_ORIGIN");
  char *gitCommit = getenv("GIT_COMMIT");
  char *groupId = getenv("GROUPID");
  char *artifactId = getenv("ARTIFACTID");
  char *version = getenv("VERSION");
  char *build_type = getenv("BUILD_TYPE");
  char *source_dir = getenv("SOURCE_DIR"); 
  char *build_dir = getenv("BUILD_DIR");
  
  char *s = NULL;
  int returncode = 0;

  json_t *root = json_object();
  json_t *json_arr = json_array();

  printf("GIT_ORIGIN = %s\n", gitOrigin);
  printf("GIT_COMMIT = %s\n", gitCommit);
  printf("GROUPID    = %s\n", groupId);
  printf("ARTIFACTID = %s\n", artifactId);
  printf("VERSION    = %s\n", version);
  printf("BUILD_TYPE = %s\n", build_type);
  printf("SOURCE_DIR = %s\n", source_dir);
  printf("BUILD_DIR  = %s\n", build_dir);

  json_object_set_new( root, "destID", json_integer( 1 ) );
  json_object_set_new( root, "command", json_string("enable") );
  json_object_set_new( root, "respond", json_integer( 0 ));
  json_object_set_new( root, "data", json_arr );

  json_array_append( json_arr, json_integer(11) );
  json_array_append( json_arr, json_integer(12) );
  json_array_append( json_arr, json_integer(14) );
  json_array_append( json_arr, json_integer(9) );

  s = json_dumps(root, 0);

  puts(s);
  json_decref(root);

  returncode = 0;
  printf("Returning: %d\n", returncode);
  return returncode;
}


