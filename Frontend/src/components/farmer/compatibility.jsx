import { useState } from "react"

export default function BreedingForm({ onSubmit }) {
 const [formData, setFormData] = useState({
  Cow_Breed: "",
  Cow_Age: "",
  Cow_Weight: "",
  Cow_Height: "",
  Cow_Milk_Yield: "",
  Cow_Health_Status: "",
  Cow_Drought_Resistance: "",
  Cow_Temperament: "",
  Bull_Breed: "",
  Bull_Age: "",
  Bull_Weight: "",
  Bull_Height: "",
  Bull_Health_Status: "",
  Bull_Mother_Milk_Yield: "",
  Bull_Drought_Resistance: "",
  Bull_Temperament: "",
  Same_Parents: "",
  Trait_Difference: "",
  Genetic_Diversity: "",
  Fertility_Rate: "",
  Breeding_Success_Rate: "",
  Disease_Resistance_Score: "",
  Market_Value: "",
  Past_Breeding_Success: "",
  Bull_Past_Breeding_Success: "",
  Cow_Past_Breeding_Success: "",
  Bull_Fertility_Rate: "",
  Cow_Fertility_Rate: "",
  Bull_Breeding_Success_Rate: "",
  Cow_Breeding_Success_Rate: "",
  Bull_Market_Value: "",
  Cow_Market_Value: "",
  Cow_Mother_Milk_Yield: ""
 })

 const handleChange = e => {
  const { name, value } = e.target
  setFormData(prev => ({ ...prev, [name]: value }))
 }

 const handleSubmit = e => {
  e.preventDefault()
  onSubmit(formData)
 }

 return (
  <form onSubmit={handleSubmit} className="max-w-4xl mx-auto p-6 bg-white shadow-md rounded-2xl grid grid-cols-1 md:grid-cols-2 gap-4">
   <h2 className="col-span-full text-2xl font-bold text-green-700 mb-4">Breeding Data Form</h2>
   {Object.keys(formData).map(key => (
    <div key={key} className="flex flex-col">
     <label htmlFor={key} className="text-sm font-medium text-green-700 mb-1 capitalize">
      {key.replace(/_/g, " ")}
     </label>
     <input
      type="text"
      id={key}
      name={key}
      value={formData[key]}
      onChange={handleChange}
      className="p-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
      required
     />
    </div>
   ))}
   <button
    type="submit"
    className="col-span-full mt-4 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-all"
   >
    Submit
   </button>
  </form>
 )
}
