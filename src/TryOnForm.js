import React, { useState } from "react";
import { tryOn } from "../api/api";

function TryOnForm() {
  const [person, setPerson] = useState(null);
  const [cloth, setCloth] = useState(null);

  const handleSubmit = async () => {
    const formData = new FormData();
    formData.append("person", person);
    formData.append("cloth", cloth);

    await tryOn(formData);
    alert("Done!");
  };

  return (
    <div>
      <input type="file" onChange={(e) => setPerson(e.target.files[0])} />
      <input type="file" onChange={(e) => setCloth(e.target.files[0])} />
      <button onClick={handleSubmit}>Try On</button>
    </div>
  );
}

export default TryOnForm;
