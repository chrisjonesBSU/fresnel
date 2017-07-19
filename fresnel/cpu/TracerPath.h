// Copyright (c) 2016-2017 The Regents of the University of Michigan
// This file is part of the Fresnel project, released under the BSD 3-Clause License.

#ifndef TRACER_PATH_H_
#define TRACER_PATH_H_

#include "embree_platform.h"
#include <embree2/rtcore.h>
#include <embree2/rtcore_ray.h>
#include <pybind11/pybind11.h>

#include "Tracer.h"

namespace fresnel { namespace cpu {

//! Path tracer
/*! The path tracer randomly samples light paths in the scene to obtain soft lighting from area light sources
    and other global illumination techniques (reflection, refraction, anti-aliasing, etc...).

    Every time render() is called, a sample is taken and the output updated to match the current average. Many
    samples may be needed to obtain a converged image. Call reset() to clear the current image and start a new
    sampling run. The Tracer does not know when the camera angle, materials, or other properties of the scene
    have changed, so the caller must call reset() whenever needed to start sampling a new view or changed
    scene (unless motion blur or other multiple exposure techniques are the desired output).
*/
class TracerPath : public Tracer
    {
    public:
        //! Constructor
        TracerPath(std::shared_ptr<Device> device, unsigned int w, unsigned int h, unsigned int light_samples);
        //! Destructor
        virtual ~TracerPath();

        //! Render a scene
        virtual void render(std::shared_ptr<Scene> scene);

        //! Reset the sampling
        virtual void reset();

        //! Get the number of samples taken
        unsigned int getNumSamples() const
            {
            return m_n_samples;
            }

        //! Set the random number seed
        void setSeed(unsigned int seed)
            {
            m_seed=seed;
            }

        //! Get the random number seed
        unsigned int getSeed() const
            {
            return m_seed;
            }

        //! Set the number of light samples
        void setLightSamples(unsigned int light_samples)
            {
            m_light_samples = light_samples;
            }
    protected:
        unsigned int m_n_samples;   //!< Number of samples taken since the last reset
        unsigned int m_seed;        //!< Random number seed
        unsigned int m_light_samples; //!< Number of light samples to take each render()
    };

//! Export TracerDirect to python
void export_TracerPath(pybind11::module& m);

} } // end namespace fresnel::cpu

#endif