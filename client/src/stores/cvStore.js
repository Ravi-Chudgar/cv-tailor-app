import { create } from 'zustand'

export const useCVStore = create((set) => ({
  cvs: [],
  selectedCV: null,
  jobDescription: null,
  tailoredCV: null,
  atsScore: null,
  isLoading: false,

  setCVs: (cvs) => set({ cvs }),

  setSelectedCV: (cv) => set({ selectedCV: cv }),

  setJobDescription: (jobDescription) => set({ jobDescription }),

  setTailoredCV: (tailoredCV) => set({ tailoredCV }),

  setATSScore: (atsScore) => set({ atsScore }),

  setLoading: (isLoading) => set({ isLoading }),

  clearTailoringData: () =>
    set({
      tailoredCV: null,
      atsScore: null,
    }),
}))
