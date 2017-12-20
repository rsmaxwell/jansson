/*
 *  Simple example of a CUnit unit test.
 *
 *  This program (crudely) demonstrates a very simple "black box"
 *  test of the standard library functions fprintf() and fread().
 *  It uses suite initialization and cleanup functions to open
 *  and close a common temporary file used by the test functions.
 *  The test functions then write to and read from the temporary
 *  file in the course of testing the library functions.
 *
 *  The 2 test functions are added to a single CUnit suite, and
 *  then run using the CUnit Basic interface.  The output of the
 *  program (on CUnit version 2.0-2) is:
 *
 *           CUnit : A Unit testing framework for C.
 *           http://cunit.sourceforge.net/
 *
 *       Suite: Suite_1
 *         Test: test of fprintf() ... passed
 *         Test: test of fread() ... passed
 *
 *       --Run Summary: Type      Total     Ran  Passed  Failed
 *                      suites        1       1     n/a       0
 *                      tests         2       2       2       0
 *                      asserts       5       5       5       0
 */

#include <stdio.h>
#include <string.h>
#include "CUnit/Basic.h"
#include <jansson.h>

/* Pointer to the file used by the tests. */
static FILE* temp_file = NULL;

/* The suite initialization function.
 * Opens the temporary file used by the tests.
 * Returns zero on success, non-zero otherwise.
 */
int init_suite1(void) {
   if (NULL == (temp_file = fopen("temp.txt", "w+"))) {
      return -1;
   }
   else {
      return 0;
   }
}

/* The suite cleanup function.
 * Closes the temporary file used by the tests.
 * Returns zero on success, non-zero otherwise.
 */
int clean_suite1(void) {
   if (0 != fclose(temp_file)) {
      return -1;
   }
   else {
      temp_file = NULL;
      return 0;
   }
}

/* Simple test of fprintf().
 * Writes test data to the temporary file and checks
 * whether the expected number of bytes were written.
 */
void testFPRINTF(void) {
   int i1 = 10;

   if (NULL != temp_file) {
      CU_ASSERT(0 == fprintf(temp_file, ""));
      CU_ASSERT(2 == fprintf(temp_file, "Q\n"));
      CU_ASSERT(7 == fprintf(temp_file, "i1 = %d", i1));
   }
}

/* Simple test of fread().
 * Reads the data previously written by testFPRINTF()
 * and checks whether the expected characters are present.
 * Must be run after testFPRINTF().
 */
void testFREAD(void)
{
   unsigned char buffer[20];

   if (NULL != temp_file) {
      rewind(temp_file);
      CU_ASSERT(9 == fread(buffer, sizeof(unsigned char), 20, temp_file));
      CU_ASSERT(0 == strncmp(buffer, "Q\ni1 = 10", 9));
   }
}

/* Simple test of fread().
 * Reads the data previously written by testFPRINTF()
 * and checks whether the expected characters are present.
 * Must be run after testFPRINTF().
 */
void testJansson(void) {
  char *s = NULL;
  int returncode = 0;

  json_t *root = json_object();
  json_t *json_arr = json_array();
  json_t *root2;
  size_t flags;
  json_error_t error;
  json_t *destID;
  int destID_value;

  json_object_set_new( root, "destID", json_integer( 1 ) );
  json_object_set_new( root, "command", json_string("enable") );
  json_object_set_new( root, "respond", json_integer( 0 ));
  json_object_set_new( root, "data", json_arr );

  json_array_append( json_arr, json_integer(11) );
  json_array_append( json_arr, json_integer(12) );
  json_array_append( json_arr, json_integer(14) );
  json_array_append( json_arr, json_integer(9) );

  s = json_dumps(root, 0);

  // puts(s);
  json_decref(root);

  flags = 0;
  root2 = json_loads(s, flags, &error);

  destID = json_object_get(root2, "destID");
  if (!json_is_integer(destID)) {
      CU_FAIL("destID is not an integer");
  }
  destID_value = (int) json_number_value(destID);
  CU_ASSERT(1 == destID_value);
}

/* Simple janson_loads.
 */
void testJsonLoads(void)
{
    json_t *rootJson;
    json_t *nameJson;
    json_error_t error;
    char *text = "{ \"name\":\"fred\" }";
    const char *name = NULL;

    rootJson = json_loads(text, 0, &error);

    if (!rootJson) {
        printf("error on line %d: %s\n", error.line, error.text);
        CU_FAIL("json_loads failed (1)");
    }

    nameJson = json_object_get(rootJson, "name");
    if (!json_is_string(nameJson)) {
        printf("error 'name' field is not a string\n");
        json_decref(rootJson);
        CU_FAIL("json_loads failed (2)");
    }

    name = json_string_value(nameJson);
    if (name == NULL) {
        printf("error 'name' field cannot get the string value\n");
        json_decref(rootJson);
        CU_FAIL("Cannot get string value");
    }

    if (strcmp(name, "fred") != 0) {
        printf("error getting value of 'name' field\n");
        json_decref(rootJson);
        CU_FAIL("Got wrong string value");
    }
}


/* Simple janson_loads.
 */
void testJsonLoadf(void)
{
    json_t *rootJson;
    json_t *nameJson;
    json_error_t error;
    char *text = "{ \"name\":\"fred\" }";
    const char *name = NULL;
    char message[256];

    FILE *fp = fopen("data.json", "w");
    if (fp == NULL) {
        CU_FAIL("error opening test data for writing");
    }

    fprintf(fp, "{ \"name\":\"fred\" }");
    fclose(fp);

    fp = fopen("data.json", "r");
    if (fp == NULL) {
        CU_FAIL("error opening test data for reading");
    }

    rootJson = json_loadf(fp, 0, &error);
    fclose(fp);
    if (!rootJson) {
        sprintf(message, "json_loadf failed on line %d: %s\n", error.line, error.text);
        CU_FAIL(message);
    }

    nameJson = json_object_get(rootJson, "name");
    if (!json_is_string(nameJson)) {
        json_decref(rootJson);
        CU_FAIL("json error on field 'name': not a string");
    }

    name = json_string_value(nameJson);
    if (name == NULL) {
        json_decref(rootJson);
        CU_FAIL("Cannot get string value for json field 'name'");
    }

    if (strcmp(name, "fred") != 0) {
        json_decref(rootJson);
        sprintf(message, "Got wrong string value for json field 'name'. Got '%s' expected '%s'", name, "fred");
        CU_FAIL(message);
    }
}

/* The main() function for setting up and running the tests.
 * Returns a CUE_SUCCESS on successful running, another
 * CUnit error code on failure.
 */
int main() {
   int exitCode = 0;
   int CU_error = 0;
   int numberOfFailures = 0;
   CU_pSuite pSuite = NULL;

   /* initialize the CUnit test registry */
   if (CUE_SUCCESS != CU_initialize_registry())
      return CU_get_error();

   /* add a suite to the registry */
   pSuite = CU_add_suite("Suite_1", init_suite1, clean_suite1);
   if (NULL == pSuite) {
      CU_cleanup_registry();
      return CU_get_error();
   }

   /* add the tests to the suite */
   /* NOTE - ORDER IS IMPORTANT - MUST TEST fread() AFTER fprintf() */
   if ((NULL == CU_add_test(pSuite, "test of fprintf()", testFPRINTF)) ||
       (NULL == CU_add_test(pSuite, "test of fread()", testFREAD)) ||
       (NULL == CU_add_test(pSuite, "test of Jansson()", testJansson)) ||
       (NULL == CU_add_test(pSuite, "test of json_loads()", testJsonLoads)) ||
       (NULL == CU_add_test(pSuite, "test of json_loadf()", testJsonLoadf)))
   {
      CU_cleanup_registry();
      return CU_get_error();
   }

   /* Run all tests using the CUnit Basic interface */
   CU_basic_set_mode(CU_BRM_VERBOSE);
   CU_basic_run_tests();


   numberOfFailures =  CU_get_number_of_failures();
   if (numberOfFailures != 0) {
      exitCode = 1;
   }

   CU_cleanup_registry();
   CU_error = CU_get_error();
   if (CU_error != 0) {
      printf("CU_error = %d\n", CU_error);
      exitCode = 2;
   }
   return exitCode;
}
