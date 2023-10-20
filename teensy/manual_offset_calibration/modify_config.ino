
// void editOffset(String leg, String joint, float newOffset) {
//   if (strcmp(leg, "LF") == 0) {
//     Serial.println("Left Front leg selected.");
//     if (strcmp(joint, "hip") == 0) {
//       offSet40 = newOffset;
//     }
//     else if (strcmp(joint, "shoulder") == 0) {
//       offSet51 = newOffset;
//     }
//     else if (strcmp(joint, "knee") == 0) {
//       offSet50 = newOffset;
//     }
//   }
//   else if (strcmp(leg, "LB") == 0) {
//     Serial.print("Left Back leg selected.");
//     if (strcmp(joint, "hip") == 0) {
//       offSet41 = newOffset;
//     }
//     else if (strcmp(joint, "shoulder") == 0) {
//       offSet61 = newOffset;
//     }
//     else if (strcmp(joint, "knee") == 0) {
//       offSet60 = newOffset;
//     }
//   }
//   else if (strcmp(leg, "RF") == 0) {
//     Serial.print("Right Front leg selected.");
//     if (strcmp(joint, "hip") == 0) {
//       offSet10 = newOffset;
//     }
//     else if (strcmp(joint, "shoulder") == 0) {
//       offSet21 = newOffset;
//     }
//     else if (strcmp(joint, "knee") == 0) {
//       offSet20 = newOffset;
//     }
//   }
//   else if (strcmp(leg, "RB") == 0) {
//     Serial.print("Right Back leg selected.");
//     if (strcmp(joint, "hip") == 0) {
//       offSet11 = newOffset;
//     }
//     else if (strcmp(joint, "shoulder") == 0) {
//       offSet31 = newOffset;
//     }
//     else if (strcmp(joint, "knee") == 0) {
//       offSet30 = newOffset;
//     }
//   }
//   else {
//     Serial.println("Invalid identifier. Process cancelled.");
//   }
// }

void editOffset(String leg, String joint, String direction, float offsetDelta) {
  int direction_constant = 1;
  if (leg == "LF") {
    Serial.println("Left Front leg selected.");
    if (joint == "hip") {
      if (direction == "F") {
        direction_constant = -1;
      }
      offSet40 = offSet40 + (offsetDelta * direction_constant);
    }
    else if (joint == "shoulder") {
      if (direction == "F") {
        direction_constant = -1;
      }
      offSet51 = offSet51 + (offsetDelta * direction_constant);
    }
    else if (joint == "knee") {
      if (direction == "B") {
        direction_constant = -1;
      }
      offSet50 = offSet50 + (offsetDelta * direction_constant);
    }
  } 
  else if (leg == "LB") {
    Serial.print("Left Back leg selected.");
    if (joint == "hip") {
      if (direction == "F") {
        direction_constant = -1;
      }
      offSet41 = offSet41 + (offsetDelta * direction_constant);
    }
    else if (joint == "shoulder") {
      if (direction == "F") {
        direction_constant = -1;
      }
      offSet61 = offSet61 + (offsetDelta * direction_constant);
    }
    else if (joint == "knee") {
      if (direction == "B") {
        direction_constant = -1;
      }
      offSet60 = offSet60 + (offsetDelta * direction_constant);
    }
  }
  else if (leg == "RF") {
    Serial.print("Right Front leg selected.");
    if (joint == "hip") {
      if (direction == "B") {
        direction_constant = -1;
      }
      offSet10 = offSet10 + (offsetDelta * direction_constant);
    }
    else if (joint == "shoulder") {
      if (direction == "B") {
        direction_constant = -1;
      }
      offSet21 = offSet21 + (offsetDelta * direction_constant);
    }
    else if (joint == "knee") {
      if (direction == "F") {
        direction_constant = -1;
      }
      offSet20 = offSet20 + (offsetDelta * direction_constant);
    }
  }
  else if (leg == "RB") {
    Serial.print("Right Back leg selected.");
    if (joint == "hip") {
      if (direction == "B") {
        direction_constant = -1;
      }
      offSet11 = offSet11 + (offsetDelta * direction_constant);
    }
    else if (joint == "shoulder") {
      if (direction == "B") {
        direction_constant = -1;
      }
      offSet31 = offSet31 + (offsetDelta * direction_constant);
    }
    else if (joint == "knee") {
      if (direction == "F") {
        direction_constant = -1;
      }
      offSet30 = offSet30 + (offsetDelta * direction_constant);
    }
  }
  else {
    Serial.println("Invalid identifier. Process cancelled.");
  }
}