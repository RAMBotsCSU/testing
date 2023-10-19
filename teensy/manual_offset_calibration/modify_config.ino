
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

void editOffset(String leg, String joint, float newOffset) {

  if (leg == "LF") {
    Serial.println("Left Front leg selected.");
    if (joint == "hip") {
      offSet40 = newOffset;
    }
    else if (joint == "shoulder") {
      offSet51 = newOffset;
    }
    else if (joint == "knee") {
      offSet50 = newOffset;
    }
  } 
  else if (leg == "LB") {
    Serial.print("Left Back leg selected.");
    if (joint == "hip") {
      offSet41 = newOffset;
    }
    else if (joint == "shoulder") {
      offSet61 = newOffset;
    }
    else if (joint == "knee") {
      offSet60 = newOffset;
    }
  }
  else if (leg == "RF") {
    Serial.print("Right Front leg selected.");
    if (joint == "hip") {
      offSet10 = newOffset;
    }
    else if (joint == "shoulder") {
      offSet21 = newOffset;
    }
    else if (joint == "knee") {
      offSet20 = newOffset;
    }
  }
  else if (leg == "RB") {
    Serial.print("Right Back leg selected.");
    if (joint == "hip") {
      offSet11 = newOffset;
    }
    else if (joint == "shoulder") {
      offSet31 = newOffset;
    }
    else if (joint == "knee") {
      offSet30 = newOffset;
    }
  }
  else {
    Serial.println("Invalid identifier. Process cancelled.");
  }
}