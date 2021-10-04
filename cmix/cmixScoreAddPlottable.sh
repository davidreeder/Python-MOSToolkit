#!/bin/bash
#
# cmixScoreAddPlottable.sh
#
# Append plottable() after instances of maketable().
# Grab handle from context and enumerate tables via comments.
#
# ASSUMES  maketable() statement and assignment happen on one line. 
#

VERSION="0.1"   #RELEASE


cat $* |

  awk '
  BEGIN  {
    count = 0
  }

  /.*maketable/  {
    handle = $1
    plotcmd = sprintf("\n\t\t\t\t\t\t\t\t;plottable(%s)\t//--%d", handle, ++count)
    printf("%s\t\t%s\n", $0, plotcmd)
  }

  ! /.*maketable/  { print }
  '

