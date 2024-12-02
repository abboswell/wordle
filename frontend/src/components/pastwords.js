// import React, { useState, useEffect } from "react";
// import Modal from "react-modal";
// import {
//   Chart as ChartJS,
//   CategoryScale,
//   LinearScale,
//   PointElement,
//   LineElement,
//   Title,
//   Tooltip,
//   Legend,
// } from "chart.js";
// import { Line } from "react-chartjs-2";
// import { gamma } from "mathjs"; // Accurate Gamma function

// // Set the app element for React Modal
// Modal.setAppElement("#root");

// // Register Chart.js components
// ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

// // Beta PDF Function
// const betaPDF = (x, alpha, beta) => {
//   if (x <= 0 || x >= 1) return 0;
//   if (alpha <= 0 || beta <= 0) {
//     console.error(`Invalid alpha or beta values: alpha=${alpha}, beta=${beta}`);
//     throw new Error("Alpha and Beta must be positive numbers");
//   }
//   const betaNorm = gamma(alpha) * gamma(beta) / gamma(alpha + beta);
//   return (Math.pow(x, alpha - 1) * Math.pow(1 - x, beta - 1)) / betaNorm;
// };

// const PastWords = ({ history }) => {
//   const [isModalOpen, setIsModalOpen] = useState(false);
//   const [chartData, setChartData] = useState(null);
//   const [selectedWord, setSelectedWord] = useState(null);

//   useEffect(() => {
//     if (isModalOpen) {
//       console.log("Modal opened for word:", selectedWord);
//     }
//   }, [isModalOpen]);

//   const fetchBetaDistribution = async (word) => {
//     try {
//       const response = await fetch(`http://127.0.0.1:5000/prior-betas/${word}`);
//       const data = await response.json();

//       if (data.error || data.alpha <= 0 || data.beta <= 0) {
//         console.error(`Invalid alpha or beta received for word "${word}":`, data);
//         return;
//       }

//       console.log("Beta Distribution data:", data);

//       const alpha = data.alpha;
//       const beta = data.beta;

//       const x = Array.from({ length: 1000 }, (_, i) => i / 1000);
//       const y = x.map((val) => betaPDF(val, alpha, beta));

//       setChartData({
//         labels: x,
//         datasets: [
//           {
//             label: `Beta(${alpha}, ${beta}) for ${data.word}`,
//             data: y,
//             borderColor: "rgba(75, 192, 192, 1)",
//             backgroundColor: "rgba(75, 192, 192, 0.2)",
//             borderWidth: 2,
//           },
//         ],
//       });

//       setSelectedWord(word);
//       setIsModalOpen(true);
//     } catch (error) {
//       console.error("Error fetching beta distribution:", error);
//     }
//   };

//   return (
//     <div className="shared-table-container">
//       <h3>Past Words Predicted</h3>
//       <table className="shared-table">
//         <thead>
//           <tr>
//             <th>Word</th>
//             <th>Score</th>
//             <th>Entropy</th>
//             <th>Thompson Sample</th>
//             <th>Prior</th>
//           </tr>
//         </thead>
//         <tbody>
//           {history && history.length > 0 ? (
//             history.map((item, index) => (
//               <tr key={index}>
//                 <td>{item.word}</td>
//                 <td>{item.score.toFixed(6)}</td>
//                 <td>{item.entropy.toFixed(6)}</td>
//                 <td>
//                   <button
//                     style={{
//                       border: "none",
//                       background: "transparent",
//                       color: "blue",
//                       cursor: "pointer",
//                       textDecoration: "underline",
//                     }}
//                     onClick={() => fetchBetaDistribution(item.word)}
//                   >
//                     {item.thompsonSample.toFixed(6)}
//                   </button>
//                 </td>
//                 <td>{item.prior.toFixed(6)}</td>
//               </tr>
//             ))
//           ) : (
//             <tr>
//               <td colSpan="5">No words guessed yet.</td>
//             </tr>
//           )}
//         </tbody>
//       </table>

//       <Modal
//         isOpen={isModalOpen}
//         onRequestClose={() => setIsModalOpen(false)}
//         contentLabel="Beta Distribution"
//         className="beta-modal"
//         overlayClassName="modal-overlay"
//       >
//         <h2>Beta Distribution for {selectedWord}</h2>
//         {chartData ? (
//           <Line
//             data={chartData}
//             options={{
//               responsive: true,
//               plugins: {
//                 legend: {
//                   position: "top",
//                 },
//                 title: {
//                   display: true,
//                   text: `Beta Distribution for ${selectedWord}`,
//                 },
//               },
//               scales: {
//                 x: { title: { display: true, text: "Probability" } },
//                 y: { title: { display: true, text: "Density" } },
//               },
//             }}
//           />
//         ) : (
//           <p>Loading...</p>
//         )}
//         <button onClick={() => setIsModalOpen(false)}>Close</button>
//       </Modal>
//     </div>
//   );
// };

// export default PastWords;






import React, { useState } from "react";
import Modal from "react-modal";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";

// Set the app element for React Modal
Modal.setAppElement("#root");

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const betaPDF = (x, alpha, beta) => {
    const gamma = (n) => Math.sqrt(2 * Math.PI / n) * Math.pow(n / Math.E, n); // Approximation for Gamma function
    const betaNorm = gamma(alpha) * gamma(beta) / gamma(alpha + beta);
    return (Math.pow(x, alpha - 1) * Math.pow(1 - x, beta - 1)) / betaNorm;
  };

const PastWords = ({ history }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [chartData, setChartData] = useState(null);
  const [selectedWord, setSelectedWord] = useState(null);

  const fetchBetaDistribution = async (word) => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/prior-betas/${word}`);
      const data = await response.json();
      if (data.error) {
        console.error(data.error);
        return;
      }

      console.log("Beta Distribution data:", data);

      // Generate data for the beta distribution
      const alpha = data.alpha;
      const beta = data.beta;

      const x = Array.from({ length: 100 }, (_, i) => i / 100); // x-axis values: [0, 0.01, ..., 1]
      const y = x.map((val) => betaPDF(val, alpha, beta));

      setChartData({
        labels: x,
        datasets: [
          {
            label: `Beta(${data.alpha}, ${data.beta}) for ${data.word}`,
            data: y,
            borderColor: "rgba(75, 192, 192, 1)",
            backgroundColor: "rgba(75, 192, 192, 0.2)",
            borderWidth: 2,
          },
        ],
      });

      setSelectedWord(word);
      setIsModalOpen(true);
    } catch (error) {
      console.error("Error fetching beta distribution:", error);
    }
  };

  const handleGuessSubmit = (e) => {
    e.preventDefault(); // Prevent default form behavior
    console.log("Guess submitted."); // Debugging Guess Submission
    // Add any guess submission logic here
  };


  return (
    <div className="shared-table-container">
      <h3>Past Words Predicted</h3>
      <table className="shared-table">
        <thead>
          <tr>
            <th>Word</th>
            <th>Score</th>
            <th>Entropy</th>
            <th>Thompson Sample</th>
            <th>Prior</th>
          </tr>
        </thead>
        <tbody>
          {history && history.length > 0 ? (
            history.map((item, index) => (
              <tr key={index}>
                <td>{item.word}</td>
                <td>{item.score.toFixed(6)}</td>
                <td>{item.entropy.toFixed(6)}</td>
                <td>
                  <button
                    style={{
                      border: "none",
                      background: "transparent",
                      color: "blue",
                      cursor: "pointer",
                      textDecoration: "underline",
                    }}
                    onClick={() => fetchBetaDistribution(item.word)}
                  >
                    {item.thompsonSample.toFixed(6)}
                  </button>
                </td>
                <td>{item.prior.toFixed(6)}</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="5">No words guessed yet.</td>
            </tr>
          )}
        </tbody>
      </table>

      {/* Modal for Beta Distribution */}
      <Modal
        isOpen={isModalOpen}
        onRequestClose={() => setIsModalOpen(false)}
        contentLabel="Beta Distribution"
        className="beta-modal"
        overlayClassName="modal-overlay"
      >
        <h2>Beta Distribution for {selectedWord}</h2>
        {chartData ? (
          <Line
            data={chartData}
            options={{
              responsive: true,
              plugins: {
                legend: {
                  position: "top",
                },
                title: {
                  display: true,
                  text: `Beta Distribution for ${selectedWord}`,
                },
              },
              scales: {
                x: { title: { display: true, text: "Probability" } },
                y: { title: { display: true, text: "Density" } },
              },
            }}
          />
        ) : (
          <p>Loading...</p>
        )}
        <button onClick={() => setIsModalOpen(false)}>Close</button>
      </Modal>
    </div>
  );
};

export default PastWords;

