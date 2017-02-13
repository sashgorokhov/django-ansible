from django import dispatch

task_finished = dispatch.Signal(['task'])
task_started = dispatch.Signal(['task'])

play_started = dispatch.Signal(['play'])
play_finished = dispatch.Signal(['play'])
