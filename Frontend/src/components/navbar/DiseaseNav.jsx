import React from "react";
import { Link, useLocation } from "react-router-dom";

const DiseaseNav = () => {
  const location = useLocation();
  const currentPath = location.pathname;
  
  return (
    <div className="flex items-center  gap-8  pb-2">
      <Link 
        to="/farmer/disease/image" 
        className={`flex items-center gap-2 pb-1 transition-all ${
          currentPath === "/farmer/disease/image" 
            ? "text-green-600 font-bold border-b-2 border-green-500" 
            : "text-gray-700 hover:text-blue-500"
        }`}
      >
        <span className="text-lg">Disease Symptoms</span>
      </Link>
      
      <Link 
        to="/farmer/disease/question" 
        className={`flex items-center gap-2 pb-1 transition-all ${
          currentPath === "/farmer/disease/question" 
            ? "text-green-600 font-bold border-b-2 border-green-500" 
            : "text-gray-700 hover:text-blue-500"
        }`}
      >
        <span className="text-lg">Disease QnA</span>
      </Link>
    </div>
  );
};

export default DiseaseNav;