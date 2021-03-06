#!/usr/bin/env python
import traceback
import pwd
import os
from os.path import join, isfile
import subprocess
import importlib

# local imports
from code_evaluator import CodeEvaluator


class JavaCodeEvaluator(CodeEvaluator):
    """Tests the Java code obtained from Code Server"""
    def __init__(self, test_case_data, test, language, user_answer,
                     ref_code_path=None, in_dir=None):
        super(JavaCodeEvaluator, self).__init__(test_case_data, test,
                                                 language, user_answer,
                                                 ref_code_path, in_dir)
        self.test_case_args = self._setup()

    # Private Protocol ##########
    def _setup(self):
        super(JavaCodeEvaluator, self)._setup()

        ref_path, test_case_path = self._set_test_code_file_path(self.ref_code_path)
        self.submit_path = self.create_submit_code_file('Test.java')

        # Set file paths
        java_student_directory = os.getcwd() + '/'
        java_ref_file_name = (ref_path.split('/')[-1]).split('.')[0]

        # Set command variables
        compile_command = 'javac  {0}'.format(self.submit_path),
        compile_main = ('javac {0} -classpath '
                        '{1} -d {2}').format(ref_path,
                                             java_student_directory,
                                             java_student_directory)
        run_command_args = "java -cp {0} {1}".format(java_student_directory,
                                                     java_ref_file_name)
        remove_user_output = "{0}{1}.class".format(java_student_directory,
                                                     'Test')
        remove_ref_output = "{0}{1}.class".format(java_student_directory,
                                                     java_ref_file_name)

        return (ref_path, self.submit_path, compile_command, compile_main,
                     run_command_args, remove_user_output, remove_ref_output)

    def _teardown(self):
        # Delete the created file.
        super(JavaCodeEvaluator, self)._teardown()
        os.remove(self.submit_path)

    def _check_code(self, ref_code_path, submit_code_path, compile_command,
                     compile_main, run_command_args, remove_user_output,
                     remove_ref_output):
        """ Function validates student code using instructor code as
        reference.The first argument ref_code_path, is the path to
        instructor code, it is assumed to have executable permission.
        The second argument submit_code_path, is the path to the student
        code, it is assumed to have executable permission.

        Returns
        --------

        returns (True, "Correct answer") : If the student function returns
        expected output when called by reference code.

        returns (False, error_msg): If the student function fails to return
        expected output when called by reference code.

        Returns (False, error_msg): If mandatory arguments are not files or
        if the required permissions are not given to the file(s).

        """
        if not isfile(ref_code_path):
            return False, "No file at %s or Incorrect path" % ref_code_path
        if not isfile(submit_code_path):
            return False, 'No file at %s or Incorrect path' % submit_code_path

        success = False
        ret = self._compile_command(compile_command)
        proc, stdnt_stderr = ret
        stdnt_stderr = self._remove_null_substitute_char(stdnt_stderr)

        # Only if compilation is successful, the program is executed
        # And tested with testcases
        if stdnt_stderr == '':
            ret = self._compile_command(compile_main)
            proc, main_err = ret
            main_err = self._remove_null_substitute_char(main_err)

            if main_err == '':
                ret = self._run_command(run_command_args, shell=True,
                                         stdin=None,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
                proc, stdout, stderr = ret
                if proc.returncode == 0:
                    success, err = True, "Correct answer"
                else:
                    err = stdout + "\n" + stderr
                os.remove(remove_ref_output)
            else:
                err = "Error:"
                try:
                    error_lines = main_err.splitlines()
                    for e in error_lines:
                        if ':' in e:
                            err = err + "\n" + e.split(":", 1)[1]
                        else:
                            err = err + "\n" + e
                except:
                        err = err + "\n" + main_err
            os.remove(remove_user_output)
        else:
            err = "Compilation Error:"
            try:
                error_lines = stdnt_stderr.splitlines()
                for e in error_lines:
                    if ':' in e:
                        err = err + "\n" + e.split(":", 1)[1]
                    else:
                        err = err + "\n" + e
            except:
                err = err + "\n" + stdnt_stderr

        return success, err
