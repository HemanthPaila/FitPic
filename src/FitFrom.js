import React, { useState } from "react";
import { predictFit } from "../api/api";

function FitForm() {
  const [features, setFeatures] = useState([]);

  const handleSubmit = async () => {
    const res = await predictFit({ features });
    console.log(res.data);
  };

  return (
    <div>
      <button onClick={handleSubmit}>Predict Fit</button>
    </div>
  );
}

export default FitForm;
